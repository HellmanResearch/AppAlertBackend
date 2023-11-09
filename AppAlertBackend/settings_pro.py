from .settings import *

DEBUG = False


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ssv_alert_service',
        'USER': 'ssv_alert_service',
        'PASSWORD': 'ssv_alert_service,1',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}

CELERY_BROKER_URL = "amqp://ssv_alert_service:ssv_alert_service,1@localhost/ssv_alert_service",

PROM_RULE_FILE = "/projects/hellman_alert/prometheus-2.38.0.linux-amd64/rules/ssv_rules.yml"
PROM_BASE_URL = "http://127.0.0.1:9090"
PROM_ADDR = "127.0.0.1"

BASE_URL = "https://alert.hellman.team"

SSV_NODE_WS = "ws://127.0.0.1:15001"
SSV_CLUSTER_SCANNER = "/opt/alert/cluster-scanner"


SSV_ADDRESS = "0xDD9BC35aE942eF0cFa76930954a156B3fF30a4E1"
SSV_INIT_HEIGHT = 17507487
ETH_URL = "http://8.217.120.4:8545"
CELERY_PROMETHEUS_PORT = 9019

SSV_VIEW_ADDRESS = "0xafE830B6Ee262ba11cce5F32fDCd760FFE6a66e4"
SSV_OPERATOR_BASE_URL = "https://api.ssv.network/api/v4/mainnet/operators/"
