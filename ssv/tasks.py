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

from . import models as l_models

logger = logging.getLogger("tasks")

sync_decided_lock = Lock()
process_decided_to_operator_decided_lock = Lock()


@shared_task
def sync_decided():
    is_got = sync_decided_lock.acquire(timeout=1)
    if is_got is False:
        return
    try:
        logger.info("got lock")
        with connect(f"{settings.SSV_NODE_WS}/stream") as websocket:
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
            for signer_str in decided.signers.split(","):
                signer = int(signer_str)
                operator_decided = l_models.OperatorDecided(decided_id=decided.id,
                                                            operator_id=signer,
                                                            height=decided.height,
                                                            missed=False,
                                                            time=decided.create_time)
                operator_decided_list.append(operator_decided)
            l_models.OperatorDecided.objects.bulk_create(operator_decided_list)
        # l_models.Tag.objects.filter(key=last_process_decided_id_key).update(value=new_last_process_decided_id)
    except Exception as exc:
        print(traceback.format_exc())
        logging.warning(f"process_decided_to_operator_decided error exc: {exc}")
    process_decided_to_operator_decided_lock.release()
