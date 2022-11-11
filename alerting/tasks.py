import datetime
import json
import logging
import time

from django.conf import settings

from celery import shared_task
from . import models as l_models

from prom import models as prom_models
from .others.send import send as l_send
from .others import crate_alert_from_prom_alert as l_crate_alert_from_prom_alert


logger = logging.getLogger(__name__)


@shared_task
def create_alert():
    alert = l_models.Alert.objects.order_by("id").first()
    max_prom_alert_id = 0
    if alert is not None:
        max_prom_alert_id = alert.prom_alert_id

    prom_alert_qs = prom_models.Alert.objects.filter(id__gt=max_prom_alert_id)
    for prom_alert in prom_alert_qs:
        l_crate_alert_from_prom_alert(prom_alert)


@shared_task
def do_action(alert_id: int):
    alert = l_models.Alert.objects.get(id=alert_id)
    for i in range(3):
        try:
            l_send(alert)
        except Exception as exc:
            logger.info(f"send failed alert_id: {alert.id} exc: {exc}")
            time.sleep(20)
        else:
            alert.has_sent = True
            alert.save()
            logger.info(f"send successful alert_id: {alert_id}")
            break


@shared_task
def first_action():
    now = datetime.datetime.now()
    after_7day = datetime.timedelta(days=7)
    alert_qs = l_models.Alert.objects.filter(has_sent=False, create_time__gt=after_7day)
    count = alert_qs.count()
    logger.info("count waiting to be sent: {}", count)
    for alert in alert_qs:
        if settings.ENV == "LOCAL":
            do_action(alert_id=alert.id)
            return
        do_action.delay(alert_id=alert.id)


@shared_task
def no_confirm_reminder():
    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(days=3)
    end_time = now - datetime.timedelta(days=1)
    alert_qs = l_models.Alert.objects.filter(has_sent=True, create_time__gt=start_time, create_time__lt=end_time)
    count = alert_qs.count()
    logger.info("no confirm count: {}", count)
    for alert in alert_qs:
        do_action.delay(alert_id=alert.id)
