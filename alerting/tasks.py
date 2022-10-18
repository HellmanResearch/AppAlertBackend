import json

import requests
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings


from celery import shared_task
from . import models as l_models


from prom import models as prom_models


@shared_task
def update_rules(x, y):
    return x + y


@transaction.atomic
def crate_alert_from_prom_alert(prom_alert: l_models):
    subscribes = l_models.Subscribe.objects.filter(rule_id=prom_alert.rule_id)
    for subscribe in subscribes:
        l_models.Alert.objects.create(subscribe=subscribe,
                                      user=subscribe.user,
                                      metric=subscribe.metric,
                                      prom_alert_id=prom_alert.id,
                                      confirmed=False
                                      )


@shared_task
def crate_alert():
    alert = l_models.Alert.objects.order_by("id").first()
    max_prom_alert_id = 0
    if alert is not None:
        max_prom_alert_id = alert.prom_alert_id

    prom_alert_qs = prom_models.Alert.objects.filter(id__gt=max_prom_alert_id)
    for prom_alert in prom_alert_qs:
        crate_alert_from_prom_alert(prom_alert)


@shared_task
def do_action(alert_id: int):
    alert = l_models.Alert.objects.get(id=alert_id)
    confirm_url = f"{settings.BASE_URL}/api/v1/alerting/alert/{alert.id}/confirm"
    if alert.subscribe.notification_type == "email":
        send_mail(
            subject="Hellman Alert",
            message=alert.subscribe.name,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[alert.subscribe.notification_address]
        )
    elif alert.subscribe.notification_type == "discord":
        request_body = {
            "content": f"Hellman Alert\nName: {alert.subscribe.name}"
        }
        headers = {
            "Content-Type": "application/json"
        }
        requests.post(url=alert.subscribe.notification_address, data=json.dumps(request_body), timeout=60)


