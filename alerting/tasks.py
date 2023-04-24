import datetime
import json
import logging
import time

import jinja2
import requests
from django.conf import settings

from celery import shared_task
from . import models as l_models

from prom import models as prom_models
from .others.send import send as l_send
from .others import crate_alert_from_prom_alert as l_crate_alert_from_prom_alert


logger = logging.getLogger("tasks")


@shared_task
def create_alert():
    alert = l_models.Alert.objects.order_by("-id").first()
    max_prom_alert_id = 0
    if alert is not None:
        max_prom_alert_id = alert.prom_alert_id

    prom_alert_qs = prom_models.Alert.objects.filter(id__gt=max_prom_alert_id)
    for prom_alert in prom_alert_qs:
        l_crate_alert_from_prom_alert(prom_alert)


@shared_task
def do_action(alert_id: int, is_first_action=False):
    alert = l_models.Alert.objects.get(id=alert_id)
    if is_first_action:
        if alert.has_sent is True:
            return

    description = ""
    template = jinja2.Template(alert.metric.alert_template)
    try:
        description = template.render(conditions=alert.subscribe.conditions)
    except Exception as exc:
        logger.error(f"render alert_template error exc: {exc}")
    for i in range(3):
        try:
            l_send(alert.subscribe.notification_type,
                   alert.subscribe.notification_address,
                   alert.id,
                   alert.subscribe.name,
                   description,
                   user_name=alert.user.public_key
                   )
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
    start_time = now - datetime.timedelta(minutes=5)
    alert_qs = l_models.Alert.objects.filter(has_sent=False, create_time__gt=start_time)
    count = alert_qs.count()
    logger.info(f"count waiting to be sent: {count}")
    for alert in alert_qs:
        if settings.ENV == "LOCAL":
            do_action(alert_id=alert.id, is_first_action=True)
            continue
        do_action.delay(alert_id=alert.id, is_first_action=True)


@shared_task
def no_confirm_reminder():
    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(days=3)
    end_time = now - datetime.timedelta(days=1)
    alert_qs = l_models.Alert.objects.filter(has_sent=True, confirmed=False, create_time__gt=start_time, create_time__lt=end_time)
    count = alert_qs.count()
    logger.info("no confirm count: {}", count)
    for alert in alert_qs:
        do_action.delay(alert_id=alert.id)


@shared_task
def new_subscribe_check_triggerd(subscribe_id: int):
    subscribe = l_models.Subscribe.objects.get(id=subscribe_id)
    intervals = subscribe.create_time - subscribe.rule.create_time
    intervals_seconds = intervals.total_seconds()
    if intervals_seconds < 60:
        return
    url = f"{settings.PROM_BASE_URL}/api/v1/query"
    params = {
        "query": f'ALERTS{{alertname="{subscribe.rule.id}"}}'
    }
    response = requests.get(url, params=params)
    logger.info(f"response.status_code: {response.status_code} body: {response.text}")
    if response.status_code != 200:
        raise Exception("response.status_code != 200")
    response_json = response.json()
    result = response_json["data"]["result"]
    if len(result) > 1:
        raise Exception("len(result) > 1")
    elif len(result) == 0:
        return
    l_models.Alert.objects.create(
        subscribe=subscribe,
        user=subscribe.user,
        metric=subscribe.metric,
        prom_alert_id=0,
        has_sent=False
    )






