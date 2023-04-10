import json
import logging

import django.db
from django.conf import settings

from celery import shared_task
from multiprocessing import Lock
from websockets.sync.client import connect
from django.db import IntegrityError

from . import models as l_models

logger = logging.getLogger("tasks")

sync_decided_lock = Lock()


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
