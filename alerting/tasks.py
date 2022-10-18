
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
            from_email="hellman_alert@outlook.com",
            auth_user="hellman_alert@outlook.com",
            auth_password="wonders,1"
        )
    elif alert.subscribe.notification_type == "discord":
        pass
