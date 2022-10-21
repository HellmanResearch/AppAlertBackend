import requests
import yaml
import logging

from django.conf import settings


from celery import shared_task
from . import models as l_models
from alerting import models as alerting_models


logger = logging.getLogger(__name__)


# @shared_task
# def update_rules(x, y):
#     return x + y
#
#
# @shared_task
# def match_prom_alert(prom_alert_id: int):
#     prom_alert = l_models.Alert.objects.get(id=prom_alert_id)
#     prom_alert


def update_rule():
    rule_qs = l_models.Rule.objects.filter(disabled=False)
    qs = alerting_models.Subscribe.objects.values("rule").distinct()
    subscribe_rule_id_list = [item["rule"] for item in qs]
    disabled_count = 0
    for rule in rule_qs:
        if rule.id not in subscribe_rule_id_list:
            rule.disabled = True
            rule.save()
            disabled_count += 1
    logger.info(f"disabled {disabled_count} rule")


def update_rule_to_prometheus_and_reload():
    # metric_group_qs = l_models.MetricGroup.objects.all()
    rule_qs = l_models.Rule.objects.filter(disabled=False)
    # data = {
    #     "groups": [
    #     ]
    # }
    group_map = {

    }
    count = 0
    for rule in rule_qs:
        if rule.metric.key not in group_map:
            group_map[rule.metric.key] = []
        item = {
            "alert": str(rule.id),
            "expr": rule.expr,
            "for": "1m"
        }
        group_map[item.metric.key].append(item)
        count += 1

    groups = {key: value for key, value in group_map.items()}
    data = {"groups": groups}
    with open(settings.PROM_RULE_FILE, "w") as f:
        yaml.dump(data, f)
    logger.info(f"update {rule} rules")

    reload_url = f"{settings.PROM_BASE_URL}/-/reload"
    response = requests.post(reload_url, timeout=60)
    if response.status_code != 200:
        error_info = f"Failed reload status_code: {response.status_code} body: {response.text}"
        logger.error(error_info)
        raise Exception(error_info)






