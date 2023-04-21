#!/usr/bin/env python3

import os
import sys
import socket
import subprocess
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from AppAlertBackend import project_env

# project_env.set_django_settings_env()


import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_NAME = BASE_DIR.rsplit("/", 1)[-1]
ENV_CHOICES = ("LOCAL", "DEV", "FAT", "UAT", "PT", "PRO")

ENV = os.environ.get("ENV", "LOCAL")
if ENV not in ENV_CHOICES:
    raise Exception(f"非法环境变量ENV: {ENV}")
if ENV == "LOCAL":
    settings = "{}.settings".format(APP_NAME)
else:
    if ENV not in ENV_CHOICES:
        raise Exception(f"环境变量ENV必须为{ENV_CHOICES}")
    settings = f"{APP_NAME}.settings_{ENV.lower()}"
print(f"settings: {settings}")
os.environ["DJANGO_SETTINGS_MODULE"] = settings
django.setup()

from ssv import models as ssv_models

import os
import json
import time
import random
import logging
import datetime
import traceback
import subprocess

import prometheus_client

import logging
from logging import handlers

# handler = handlers.RotatingFileHandler("all.log", mode="a", maxBytes=1024 * 1024 * 10, backupCount=5, encoding="utf-8")
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filemode='a')

metric_operator_performance_1day = prometheus_client.Gauge("operator_performance_1day",
                                                           "operator performance 1 day", ["id"])

metric_operator_performance_1month = prometheus_client.Gauge("operator_performance_1month",
                                                             "operator_performance_1month", ["id"])

metric_operator_active = prometheus_client.Gauge("operator_active",
                                                 "operator_active", ["id"])

metric_operator_fee = prometheus_client.Gauge("operator_fee",
                                              "operator_fee", ["id"])
metric_operator_status = prometheus_client.Gauge("operator_status",
                                                 "operator_status", ["id"])

metric_validator_active = prometheus_client.Gauge("validator_active",
                                                  "validator_active", ["public_key"])

metric_cluster_balance_est_days = prometheus_client.Gauge("cluster_balance_est_days",
                                                          "cluster_balance_est_days", ["id"])

metric_cluster_balance = prometheus_client.Gauge("cluster_balance",
                                                 "cluster_balance", ["id"])

metric_cluster_liquidated = prometheus_client.Gauge("cluster_liquidated",
                                                    "cluster_liquidated", ["id"])


def update_operator():
    operator_qs = ssv_models.Operator.objects.all()
    for operator in operator_qs:
        metric_operator_performance_1day.labels(id=operator.id).set(operator.performance_1day)
        metric_operator_performance_1month.labels(id=operator.id).set(operator.performance_1month)
        active_status = 1 if operator.active is True else 0
        metric_operator_active.labels(id=operator.id).set(active_status)
        metric_operator_fee.labels(id=operator.id).set(operator.fee_human)


def update_validator():
    validator_qs = ssv_models.Validator.objects.all()
    for validator in validator_qs:
        active_status = 1 if validator.active is True else 0
        metric_validator_active.labels(public_key=validator.public_key).set(active_status)


def update_cluster():
    cluster_qs = ssv_models.Cluster.objects.all()
    for cluster in cluster_qs:
        metric_cluster_liquidated.labels(id=cluster.id).set(cluster.liquidated)
        metric_cluster_balance.labels(id=cluster.id).set(cluster.balance_human)
        metric_cluster_balance_est_days.labels(id=cluster.id).set(cluster.est_days)


if __name__ == '__main__':
    prometheus_client.start_http_server(9121)
    logging.info("started")
    while True:
        try:
            update_operator()
            update_validator()
            update_cluster()
        except Exception as exc:
            logging.warning(traceback.format_exc())
        logging.info("Round end")
        time.sleep(60 * 2)
