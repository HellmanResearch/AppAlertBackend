from celery import shared_task
from . import models as l_models


@shared_task
def update_rules(x, y):
    return x + y


@shared_task
def match_prom_alert(prom_alert_id: int):
    prom_alert = l_models.Alert.objects.get(id=prom_alert_id)
    prom_alert
