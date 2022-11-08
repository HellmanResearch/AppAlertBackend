from .settings import *



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ssv_alert_service',
        'USER': 'root',
        'PASSWORD': 'wonders,1',
        'HOST': '127.0.0.1',
        'PORT': '3308'
    }
}

CELERY_BROKER_URL = "amqp://alert:alert,1@localhost/alert",
