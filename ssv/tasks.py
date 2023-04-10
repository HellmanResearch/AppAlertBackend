import datetime
import json
import logging
import traceback

import django.db
from django.conf import settings

from celery import shared_task
from multiprocessing import Lock

from django.db.models import Max
from websockets.sync.client import connect
from django.db import IntegrityError

from web3 import Web3

from django.conf import settings

from . import models as l_models
from . import others as l_others

logger = logging.getLogger("tasks")

sync_decided_lock = Lock()
process_decided_to_operator_decided_lock = Lock()


def get_validator_operators():
    validator_operators_map = {}
    operator_validator_list = l_models.OperatorValidator.objects.all()
    for operator_validator in operator_validator_list:
        validator_public_key = operator_validator.validator_public_key
        operator_id_list = validator_operators_map.get(validator_public_key)
        if operator_id_list is None:
            operator_id_list = []
        operator_id_list.append(operator_validator.operator_id)
        validator_operators_map[validator_public_key] = operator_id_list
    return validator_operators_map

        # if operator_validator.validator_public_key not in validator_operators_map.keys():
        #     validator_operators_map[operator_validator.validator_public_key] = []
        # validator_operators_map[operator_validator.validator_public_key] = validator_operators_map[operator_validator.validator_public_key] + [operator_validator.operator_id]


def get_contract():
    w3 = Web3(Web3.HTTPProvider(settings.ETH_URL))
    abi = json.loads(settings.SSV_ABI)
    contract = w3.eth.contract(address=settings.SSV_ADDRESS, abi=abi)
    return contract


def get_last_block_number():
    w3 = Web3(Web3.HTTPProvider(settings.ETH_URL))
    return w3.eth.block_number

@shared_task
def sync_decided():
    is_got = sync_decided_lock.acquire(timeout=1)
    if is_got is False:
        return
    try:
        logger.info("got lock")
        with connect(f"{settings.SSV_NODE_WS}/stream") as websocket:
            logger.info("connected")

            for _ in range(2000):
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
        logging.warning(f"sync decided error exc: {exc}")
    sync_decided_lock.release()


@shared_task
def process_decided_to_operator_decided():
    is_got = process_decided_to_operator_decided_lock.acquire(timeout=1)
    if is_got is False:
        return
    try:
        # last_process_decided_id_key = "last_process_decided_id"
        # last_process_decided_id = 0
        # try:
        #     last_process_decided_id_tag = l_models.Tag.objects.get(key=last_process_decided_id_key)
        #     last_process_decided_id = int(last_process_decided_id_tag.value)
        # except l_models.Tag.DoesNotExist as exc:
        #     l_models.Tag.objects.create(key=last_process_decided_id_key, value="0")
        validator_operators_map = get_validator_operators()
        last_process_decided_id = 0
        result = l_models.OperatorDecided.objects.aggregate(Max("decided_id"))
        if result["decided_id__max"] is not None:
            last_process_decided_id = result["decided_id__max"]
        new_last_process_decided_id = last_process_decided_id + 10000
        now = datetime.datetime.now()
        limit_time = now - datetime.timedelta(minutes=10)
        decided_qs = l_models.Decided.objects.filter(id__gte=last_process_decided_id,
                                                     id__lt=new_last_process_decided_id,
                                                     create_time__lte=limit_time)
        for decided in decided_qs:
            operator_decided_list = []
            operator_id_list = validator_operators_map.get(decided.validator_public_key)
            if operator_id_list is None:
                logger.warning(f"validator {decided.validator_public_key} not in validator_operators_map")
                continue
            # operator_id_set = set(operator_id_list)
            signer_id_list = [int(item) for item in decided.signers.split(",")]
            # missed_operator_id_list = set(operator_id_list) - set(signer_id_list)
            # logger.warning("")
            for operator_id in operator_id_list:
                missed = operator_id in signer_id_list
                operator_decided = l_models.OperatorDecided(decided_id=decided.id,
                                                            operator_id=operator_id,
                                                            height=decided.height,
                                                            missed=missed,
                                                            time=decided.create_time)

            # for signer in signer_id_list:
            #     # signer = int(signer_str)
            #     operator_decided = l_models.OperatorDecided(decided_id=decided.id,
            #                                                 operator_id=signer,
            #                                                 height=decided.height,
            #                                                 missed=False,
            #                                                 time=decided.create_time)
                operator_decided_list.append(operator_decided)
            l_models.OperatorDecided.objects.bulk_create(operator_decided_list)
        # l_models.Tag.objects.filter(key=last_process_decided_id_key).update(value=new_last_process_decided_id)
    except Exception as exc:
        print(traceback.format_exc())
        logging.warning(f"process_decided_to_operator_decided error exc: {exc}")
    process_decided_to_operator_decided_lock.release()


# @shared_task
# def sync_operator():
#     last_sync_operator_key = "last_sync_operator_block_height"
#     last_sync_operator_block_height = settings.SSV_INIT_HEIGHT
#     try:
#         tag = l_models.Tag.objects.get(key=last_sync_operator_key)
#         last_sync_operator_block_height = int(tag.value)
#     except l_models.Tag.DoesNotExist as exc:
#         l_models.Tag.objects.create(key=last_sync_operator_key, value=str(settings.SSV_INIT_HEIGHT))
#     last_block_number = l_others.contract.get_last_block_number()
#     end_last_sync_operator_block_height = last_sync_operator_block_height + 10000
#     if end_last_sync_operator_block_height > last_block_number:
#         end_last_sync_operator_block_height = last_block_number
#     contract = l_others.contract.get_contract()
#     event_filter = contract.events.ValidatorAdded.create_filter(fromBlock=last_sync_operator_block_height,
#                                                                 toBlock=end_last_sync_operator_block_height)
#     entries = event_filter.get_all_entries()
#     for event in entries:
#         try:
#             l_models.Account.objects.create(public_key=event["args"]["owner"])
#         except l_models.Account.DoesNotExist:
#             pass
#         try:
#             l_models.Operator.objects.create(public_key=event["args"]["owner"])
#         except l_models.Account.DoesNotExist:
#             pass


@shared_task
def sync_validator():
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
    contract = get_contract()
    event_filter = contract.events.ValidatorAdded.create_filter(fromBlock=last_sync_operator_block_height,
                                                                toBlock=end_last_sync_operator_block_height)
    entries = event_filter.get_all_entries()
    for event in entries:
        for operator_id in event["args"]["operatorIds"]:
            try:
                validator_public_key = "0x" + event["args"]["publicKey"].hex()
                l_models.OperatorValidator.objects.create(validator_public_key=validator_public_key, operator_id=operator_id)
            except IntegrityError:
                pass
    l_models.Tag.objects.filter(key=last_sync_operator_key).update(value=str(end_last_sync_operator_block_height))
