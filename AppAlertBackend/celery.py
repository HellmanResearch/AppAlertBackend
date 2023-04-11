import os
import logging
import threading

import wsgiserver

from django.conf import settings
from celery import Celery
# from celery.schedules import crontab
# from prometheus_client import multiprocess
# from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, Gauge, Counter

from . import project_env

logger = logging.getLogger("tasks")


settings_name = project_env.get_django_settings()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_name)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
app = Celery(project_env.APP_NAME)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'create_alert': {
        'task': 'alerting.tasks.create_alert',
        'schedule': 60
    },
    'first_action': {
        'task': 'alerting.tasks.first_action',
        'schedule': 60 * 2
    },
    'no_confirm_reminder': {
        'task': 'alerting.tasks.no_confirm_reminder',
        'schedule': 86400
    },
    'update_rule': {
        'task': 'prom.tasks.update_rule',
        'schedule': 300
    },
    'sync_decided': {
        'task': 'ssv.tasks.sync_decided',
        'schedule': 5
    },
    'process_decided_to_operator_decided': {
        'task': 'ssv.tasks.process_decided_to_operator_decided',
        'schedule': 20
    },
    'sync_operator': {
        'task': 'ssv.tasks.sync_operator',
        'schedule': 120
    },
    'sync_validator': {
        'task': 'ssv.tasks.sync_validator',
        'schedule': 120
    },
    'update_performance': {
        'task': 'ssv.tasks.update_performance',
        'schedule': 120
    },
    'delete_decided': {
        'task': 'ssv.tasks.delete_decided',
        'schedule': 60 * 60
    }
}


# def metrics(environ, start_response):
#     registry = CollectorRegistry()
#     # multiprocess.MultiProcessCollector(registry)
#     data = generate_latest(registry)
#     # return Response(data, mimetype=CONTENT_TYPE_LATEST)
#
#     status = '200 OK'
#     response_headers = [('Content-type', 'text/html; charset=utf-8')]
#     start_response(status, response_headers)
#     return [data]


# def start_server():
#     server = wsgiserver.WSGIServer(metrics, host="0.0.0.0", port=settings.CELERY_PROMETHEUS_PORT)
#     server.start()


# class PrometheusServer(threading.Thread):
#
#     def metrics(self, environ, start_response):
#         print("metricsmetricsmetricsmetricsmetrics")
#         logger.info("metricsmetricsmetricsmetricsmetrics")
#         try:
#             registry = CollectorRegistry()
#             multiprocess.MultiProcessCollector(registry)
#             data = generate_latest(registry)
#             # return Response(data, mimetype=CONTENT_TYPE_LATEST)
#
#             status = '200 OK'
#             response_headers = [('Content-type', CONTENT_TYPE_LATEST), ('Content-Length', str(len(data)))]
#             start_response(status, response_headers)
#             return [data]
#         except Exception as exc:
#             logger.warning(f"get metrics error exc: {exc}")
#
#     def run(self) -> None:
#         server = wsgiserver.WSGIServer(self.metrics, host="0.0.0.0", port=settings.CELERY_PROMETHEUS_PORT)
#         server.start()


# IS_CELERY = os.getenv("IS_CELERY")
# print(f"IS_CELERY: {IS_CELERY}")
# logger.info(f"IS_CELERY: {IS_CELERY}")
# print(f"port: {settings.CELERY_PROMETHEUS_PORT}")

# prometheus_server = PrometheusServer()
# prometheus_server.start()
# print("prometheus_server start completed")

# if os.getenv("IS_CELERY"):
#     prometheus_server = PrometheusServer()
#     prometheus_server.start()
#     print("prometheus_server start completed")