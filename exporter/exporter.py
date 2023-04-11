
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

icp_balance = prometheus_client.Gauge("dfinity_icp_balance", "Balance of ICP of Dfinity",
                                      ["account_name"])

logger = logging.getLogger("cycles_exporter")
ENV = os.getenv("ENV")

network = "ic"
project_path = "/Users/mmt/local/dfinity_project"
if ENV == "PRO":
    project_path = "/home/ops/local/WICP"


class Dfinity:
    decimals = 8
    decimals_dividend = 1e8

    def __init__(self, network, project_path):
        self.network = network
        self.project_path = project_path
        self.transaction_fee = 10000

    def run_cmd(self, cmd, timeout):
        cmd = f"cd {self.project_path};{cmd}"
        logger.info(f"run cmd: {cmd}")

        # if ENV == "LOCAL":
        #     if random.random() > 0.8:
        #         raise Exception("")
        #     return '(opt principal "jwaqi-eqaaa-aaaah-qco4q-cai")\n'

        start_time = datetime.datetime.now()
        try:
            cp = subprocess.run(cmd, shell=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"timeout ({timeout}s)")
        end_time = datetime.datetime.now()
        time_cost = (end_time - start_time).total_seconds()
        logger.info(
            f"cmd run completed  time_cost: {time_cost} cmd: {cmd} returncode: {cp.returncode} stdout: {cp.stdout}, stderr: {cp.stderr}")
        if cp.returncode != 0:
            err_msg = f"run cmd: {cmd} failed, stdout: {cp.stdout} stderr: {cp.stderr}"
            raise Exception(err_msg)
        return cp.stdout


dfinity = Dfinity("ic", project_path)


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
    prometheus_client.start_http_server(9118)
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
