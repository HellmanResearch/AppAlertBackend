import datetime
import json
import logging
import time
import traceback
import prometheus_client

import django.db
import requests
from django.conf import settings

from celery import shared_task
from multiprocessing import Lock
from websocket import create_connection


from django.db.models import Max, Count, Min, Avg
from websockets.sync.client import connect
from django.db import IntegrityError

from web3 import Web3

from django.conf import settings

from . import models as l_models
from . import others as l_others
from .others import cluster as l_cluster
from .others import contract as l_contract

logger = logging.getLogger("tasks")

sync_decided_lock = Lock()
process_decided_to_operator_decided_lock = Lock()

# metric_operator_performance_1day = prometheus_client.Gauge("operator_performance_1day",
#                                                            "operator performance 1 day", ["id"])


def get_validator_operators():
    validator_qs = l_models.Validator.objects.all()
    validator_operators_map = {validator.public_key: [operator.id for operator in validator.operators.all()] for
                               validator in validator_qs}

    return validator_operators_map


def get_last_block_number():
    w3 = Web3(Web3.HTTPProvider(settings.ETH_URL))
    return w3.eth.block_number


@shared_task
def sync_decided():
    logger.info("in sync_decided")
    is_got = sync_decided_lock.acquire(timeout=1)
    if is_got is False:
        return
    websocket = None
    try:
        logger.info("got lock")
        websocket = create_connection(f"{settings.SSV_NODE_WS}/stream")
        logger.info("connected")
        while True:
            message_str = websocket.recv()
            message_body = json.loads(message_str)
            for item in message_body["data"]:
                validator_public_key = "0x" + message_body["filter"]["publicKey"]
                height = item["Message"]["Height"]
                signers_str = ",".join([str(i) for i in item["Signers"]])
                try:
                    l_models.Decided.objects.create(validator_public_key=validator_public_key,
                                                    height=height,
                                                    signers=signers_str)
                except IntegrityError as exc:
                    decided = l_models.Decided.objects.get(validator_public_key=validator_public_key, height=height)
                    decided.delete()
                    l_models.Decided.objects.create(validator_public_key=validator_public_key,
                                                    height=height,
                                                    signers=signers_str)
    except Exception as exc:
        sync_decided_lock.release()
        logger.warning(f"sync decided error exc: {exc}")
    else:
        sync_decided_lock.release()
    if websocket is not None:
        websocket.close()


@shared_task
def process_decided_to_operator_decided():
    logger.info("in process_decided_to_operator_decided")
    is_got = process_decided_to_operator_decided_lock.acquire(timeout=1)
    if is_got is False:
        return
    failed_count = 0
    total_count = 0
    try:
        validator_operators_map = get_validator_operators()
        last_process_decided_id = 0
        result = l_models.OperatorDecided.objects.aggregate(Max("decided_id"))
        if result["decided_id__max"] is not None:
            last_process_decided_id = result["decided_id__max"]
        new_last_process_decided_id = last_process_decided_id + 10000

        min_result = l_models.Decided.objects.filter(id__gte=last_process_decided_id).aggregate(Min("id"))
        if min_result["id__min"] > new_last_process_decided_id:
            new_last_process_decided_id = min_result["id__min"] + 10000
        now = datetime.datetime.now()
        limit_time = now - datetime.timedelta(minutes=10)
        decided_qs = l_models.Decided.objects.filter(id__gte=last_process_decided_id,
                                                     id__lt=new_last_process_decided_id,
                                                     create_time__lte=limit_time)
        logger.info(f"decided_qs.count: {decided_qs.count()} last_process_decided_id: {last_process_decided_id} new_last_process_decided_id: {new_last_process_decided_id} limit_time: {limit_time}")
        for decided in decided_qs:
            total_count += 1
            operator_decided_list = []
            operator_id_list = validator_operators_map.get(decided.validator_public_key)
            if operator_id_list is None:
                logger.warning(f"validator {decided.validator_public_key} not in validator_operators_map")
                continue
            signer_id_list = [int(item) for item in decided.signers.split(",")]
            for operator_id in operator_id_list:
                missed = operator_id not in signer_id_list
                operator_decided = l_models.OperatorDecided(decided_id=decided.id,
                                                            operator_id=operator_id,
                                                            height=decided.height,
                                                            missed=missed,
                                                            time=decided.create_time)

                operator_decided_list.append(operator_decided)
            l_models.OperatorDecided.objects.bulk_create(operator_decided_list)
    except Exception as exc:
        process_decided_to_operator_decided_lock.release()
        logger.warning(f"process_decided_to_operator_decided error exc: {exc}")
        failed_count += 1
    else:
        process_decided_to_operator_decided_lock.release()
    return f"failed_count: {failed_count} total_count: {total_count}"


@shared_task
def sync_operator():
    last_sync_operator_key = "last_sync_operator_block_height"
    last_sync_operator_block_height = settings.SSV_INIT_HEIGHT
    try:
        tag = l_models.Tag.objects.get(key=last_sync_operator_key)
        last_sync_operator_block_height = int(tag.value)
    except l_models.Tag.DoesNotExist as exc:
        l_models.Tag.objects.create(key=last_sync_operator_key, value=str(settings.SSV_INIT_HEIGHT))
    last_block_number = get_last_block_number()
    end_last_sync_operator_block_height = last_sync_operator_block_height + 10000
    if end_last_sync_operator_block_height > last_block_number:
        end_last_sync_operator_block_height = last_block_number

    logger.info(f"last_sync_operator_block_height: {last_sync_operator_block_height} end_last_sync_operator_block_height: {end_last_sync_operator_block_height}")

    contract = l_contract.get_contract()
    event_filter = contract.events.OperatorAdded.create_filter(fromBlock=last_sync_operator_block_height,
                                                               toBlock=end_last_sync_operator_block_height)
    entries = event_filter.get_all_entries()
    for event in entries:
        owner_address = event["args"]["owner"]
        operator_id = event["args"]["operatorId"]
        l_models.Account.objects.get_or_create(address=owner_address)
        l_models.Operator.objects.get_or_create(id=operator_id)
    l_models.Tag.objects.filter(key=last_sync_operator_key).update(value=str(end_last_sync_operator_block_height))


@shared_task
def sync_validator():
    last_sync_validator_key = "last_sync_validator_block_height"
    last_sync_validator_block_height = settings.SSV_INIT_HEIGHT
    try:
        tag = l_models.Tag.objects.get(key=last_sync_validator_key)
        last_sync_validator_block_height = int(tag.value)
    except l_models.Tag.DoesNotExist as exc:
        l_models.Tag.objects.create(key=last_sync_validator_key, value=str(settings.SSV_INIT_HEIGHT))
    last_block_number = get_last_block_number()
    end_last_sync_validator_block_height = last_sync_validator_block_height + 10000
    if end_last_sync_validator_block_height > last_block_number:
        end_last_sync_validator_block_height = last_block_number
    contract = l_contract.get_contract()
    event_filter = contract.events.ValidatorAdded.create_filter(fromBlock=last_sync_validator_block_height,
                                                                toBlock=end_last_sync_validator_block_height)
    entries = event_filter.get_all_entries()
    for event in entries:
        operator_list = []
        validator_public_key = "0x" + event["args"]["publicKey"].hex()
        owner_address = event["args"]["owner"]

        l_models.Account.objects.get_or_create(address=owner_address)

        for operator_id in event["args"]["operatorIds"]:
            operator, is_new = l_models.Operator.objects.get_or_create(id=operator_id)
            operator_list.append(operator)
        validator, is_new = l_models.Validator.objects.get_or_create(public_key=validator_public_key)
        validator.owner_address = owner_address
        validator.operators.set(operator_list)

        l_cluster.save_cluster(event)


        # print("entries: ", entries)
        # try:
        #     operator_list = []
        #     validator_public_key = "0x" + event["args"]["publicKey"].hex()
        #     owner_address = event["args"]["owner"]
        #
        #     l_models.Account.objects.get_or_create(address=owner_address)
        #
        #     for operator_id in event["args"]["operatorIds"]:
        #         operator, is_new = l_models.Operator.objects.get_or_create(id=operator_id)
        #         operator_list.append(operator)
        #     validator, is_new = l_models.Validator.objects.get_or_create(public_key=validator_public_key)
        #     validator.owner_address = owner_address
        #     validator.operators.set(operator_list)
        # except Exception as exc:
        #     # print(traceback.format_exc())
        #     logger.error(f"add validator error exc: {exc}")

    l_models.Tag.objects.filter(key=last_sync_validator_key).update(value=str(end_last_sync_validator_block_height))


@shared_task
def update_performance():
    now = datetime.datetime.now()
    before_one_day = now - datetime.timedelta(days=1)
    decided_qs = l_models.OperatorDecided.objects.filter(time__gte=before_one_day)
    total_decided_qs = decided_qs.values("operator_id").annotate(count=Count("id"))
    not_missed_decided_qs = decided_qs.filter(missed=False).values("operator_id").annotate(count=Count("id"))

    total_decided_map = {item["operator_id"]: item["count"] for item in total_decided_qs}
    not_missed_decided_map = {item["operator_id"]: item["count"] for item in not_missed_decided_qs}

    for operator in l_models.Operator.objects.all():
        total_decided = total_decided_map.get(operator.id)
        not_missed_decided = not_missed_decided_map.get(operator.id)
        if not_missed_decided is None:
            not_missed_decided = 0

        performance = 0
        if total_decided is not None:
            performance = (not_missed_decided / total_decided) * 100
        operator.performance_1day = performance
        # metric_operator_performance_1day.labels(id=operator.id).set(performance)
        # logger.info(f"set operator: {operator.id} performance is {performance}")
        operator.save()
        l_models.OperatorPerformanceRecord.objects.create(operator=operator, performance=performance, time=now)


@shared_task
def clear_data():
    now = datetime.datetime.now()
    before_one_day = now - datetime.timedelta(days=1)
    before_one_month = now - datetime.timedelta(days=30)
    l_models.Decided.objects.filter(create_time__lte=before_one_day).delete()
    l_models.OperatorDecided.objects.filter(time__lte=before_one_day).delete()
    l_models.OperatorPerformanceRecord.objects.filter(time__lte=before_one_month).delete()


@shared_task
def update_operator_from_chain():
    operator_qs = l_models.Operator.objects.all()
    contract = l_contract.get_contract()
    failed_count = 0
    for operator in operator_qs:
        try:
            operator_info = contract.functions.operators(operator.id).call()
            operator.fee_human = operator_info[1] / 38264
            operator.validator_count = operator_info[2]
            operator.owner_address = operator_info[0]
            operator.snapshot_index = operator_info[3][1]
            operator.save()
            l_models.Account.objects.get_or_create(address=operator_info[0])
        except Exception as exc:
            logger.warning(f"update operator from chain error: operator_id {operator.id} exc: {exc}")
            failed_count += 1
    return f"failed_count: {failed_count}"


@shared_task
def update_operator_active_status():
    operator_qs = l_models.Operator.objects.all()
    now = datetime.datetime.now()
    end_time = now - datetime.timedelta(minutes=20)
    operator_id_qs = l_models.OperatorDecided.objects.filter(time__gte=end_time).values("operator_id").distinct()
    operator_id_list = [item["operator_id"] for item in operator_id_qs]
    for operator in operator_qs:
        active = False
        if operator.validator_count == 0 or operator.id in operator_id_list:
            active = True
        operator.active = active
        operator.save()


@shared_task
def update_operator_performance_month():
    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(days=30)
    performance_qs = l_models.OperatorPerformanceRecord.objects.filter(time__gte=start_time).values("operator__id")\
        .annotate(performance_avg=Avg("performance"))
    performance_map = {item["operator__id"]: item["performance_avg"] for item in performance_qs}
    for operator in l_models.Operator.objects.all():
        performance_1month = performance_map.get(operator.id)
        if performance_1month is None:
            performance_1month = 0.0
        operator.performance_1month = performance_1month
        operator.save()


@shared_task
def update_operator_name():
    operator_list = []
    base_url = f"https://api.ssv.network/api/v3/prater/operators/"
    page = 0
    page_size = 100
    while True:
        page += 1
        url = f"{base_url}?page={page}&perPage={page_size}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"response.status_code != 200 body: {response.text}")
        response_json = response.json()
        operators = response_json["operators"]
        operator_list.extend(operators)
        if len(operators) == 0 or page*page_size >= response_json["pagination"]["total"]:
            break
        time.sleep(5)

    id_name_map = {item["id"]: item["name"] for item in operator_list}
    for operator in l_models.Operator.objects.all():
        name = id_name_map.get(operator.id)
        if name is None:
            continue
        operator.name = name
        operator.save()


@shared_task
def update_cluster():
    cluster_qs = l_models.Cluster.objects.all()
    contract = l_contract.get_contract()
    view_contract = l_contract.get_view_contract()
    network_fee, network_fee_index, network_fee_index_block_number = contract.functions.network().call()
    minimum_blocks_before_liquidation = contract.functions.minimumBlocksBeforeLiquidation().call()
    minimum_liquidation_collateral = contract.functions.minimumLiquidationCollateral().call()
    if settings.ENV == "LOCAL":
        cluster_qs = cluster_qs.filter(owner="0xD1bA19ACa6A16C096ACF0B48E27Ffb8843b7FAd0")
    for cluster in cluster_qs:
        try:
            l_cluster.update_cluster(cluster, view_contract, network_fee=network_fee, network_fee_index=network_fee_index,
                                     minimum_liquidation_collateral=minimum_liquidation_collateral,
                                     minimum_blocks_before_liquidation=minimum_blocks_before_liquidation)
        except Exception as exc:
            logger.warning(f"update cluster {cluster.id} failed exc: {exc}")


@shared_task
def update_validator():
    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(minutes=30)
    validator_public_key_qs = l_models.Decided.objects.filter(create_time__gte=start_time).values("validator_public_key").distinct()
    validator_public_key_list = [item["validator_public_key"] for item in validator_public_key_qs]
    validator_qs = l_models.Validator.objects.all()
    for validator in validator_qs:
        validator.active = validator.public_key in validator_public_key_list
        validator.save()
