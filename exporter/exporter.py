
import os
import sys
import socket
import subprocess
import django


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from AppAlertBackend import project_env

project_env.set_django_settings_env()
django.setup()

import os

ENV_CHOICES = ("LOCAL", "DEV", "FAT", "UAT", "PT", "PRO")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_NAME = BASE_DIR.rsplit("/", 1)[-1]
ENV = os.environ.get("ENV", "LOCAL")
if ENV not in ENV_CHOICES:
    raise Exception(f"非法环境变量ENV: {ENV}")


def set_django_settings_env():
    if ENV == "LOCAL":
        settings = "{}.settings".format(APP_NAME)
    else:
        if ENV not in ENV_CHOICES:
            raise Exception(f"环境变量ENV必须为{ENV_CHOICES}")
        settings = f"{APP_NAME}.settings_{ENV.lower()}"
    print(f"settings: {settings}")
    os.environ["DJANGO_SETTINGS_MODULE"] = settings


from ssv import models as ssv_models

#!/usr/bin/env python3

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




def update_icp_balance():
    cmd = "dfx identity list"
    stdout = dfinity.run_cmd(cmd, timeout=10)
    account_name_list = stdout.split("\n")
    withdraw_account_name_list = [item for item in account_name_list if item.startswith("withdraw_")]

    for withdraw_account_name in withdraw_account_name_list:
        try:
            cmd = f"dfx --identity {withdraw_account_name} ledger --network ic balance"
            stdout = dfinity.run_cmd(cmd, timeout=60)
            value = stdout.split(" ICP")[0]
            value = float(value)
            icp_balance.labels(withdraw_account_name).set(value)
        except Exception as exc:
            print(exc)


if __name__ == '__main__':
    prometheus_client.start_http_server(9121)
    logger.info("started")
    while True:
        try:
            update_icp_balance()
        except Exception as exc:
            logger.warning(traceback.format_exc())

        logger.info("Round end")
        if ENV == "LOCAL":
            continue
        time.sleep(60 * 1)
