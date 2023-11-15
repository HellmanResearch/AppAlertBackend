from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ssv_alert_service_2',
        'USER': 'root',
        'PASSWORD': 'wonders,1',
        'HOST': '127.0.0.1',
        'PORT': '3308'
    }
}

CELERY_BROKER_URL = "amqp://alert:alert,1@localhost/alert",

PROM_RULE_FILE = "/opt/prometheus-2.38.0.linux-amd64/rules/ssv_rules.yml"
PROM_BASE_URL = "http://127.0.0.1:9090"
PROM_ADDR = "127.0.0.1"

BASE_URL = "http://39.101.77.40"

# hongxia.tang@aliyun.com
ETH_URL = "https://goerli.infura.io/v3/1072f8f211e2414dac30694460e39973"
DISCORD_PROXY = "http://47.88.25.203:8018/api/v1/proxy/http-json"
