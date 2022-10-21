import json
import logging
import time

import requests
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from celery import shared_task
from .. import models as l_models

from prom import models as prom_models

logger = logging.getLogger(__name__)


def send(alert: l_models.Alert):
    confirm_url = f"{settings.BASE_URL}/api/v1/alerting/alert/{alert.id}/confirm"
    content = f"Hellman Alert\nID: {alert.id}\nName: {alert.subscribe.name}\nConfirmURL: {confirm_url}"
    if alert.subscribe.notification_type == "email":
        send_mail(
            subject="Hellman Alert",
            message=content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[alert.subscribe.notification_address]
        )
    elif alert.subscribe.notification_type == "discord":
        request_body = {
            "content": content
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url=alert.subscribe.notification_address,
                                 headers=headers,
                                 data=json.dumps(request_body),
                                 timeout=60)
        logger.info(
            f"send email to {alert.subscribe.notification_address} response.status_code: {response.status_code} response.text: {response.text}")
        if response.status_code > 300:
            raise Exception("send to discord error")
    elif alert.subscribe.notification_type == "webhook":
        request_body = {
            "title": "Hellman Alert",
            "subscribe_name": alert.subscribe.name,
            "confirm_url": confirm_url
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url=alert.subscribe.notification_address,
                                 headers=headers,
                                 data=json.dumps(request_body),
                                 timeout=60)
        logger.info(
            f"send message of webhook to {alert.subscribe.notification_address} response.status_code: {response.status_code} response.text: {response.text}")
        if response.status_code > 300:
            raise Exception("send to webhook error")
    else:
        logger.error(f"unknown notification_type: {alert.subscribe.notification_type}")

