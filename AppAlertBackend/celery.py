import os

from celery import Celery

from . import project_env

settings_name = project_env.get_django_settings()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_name)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
app = Celery(project_env.APP_NAME)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'crate_alert': {
        'task': 'alerting.tasks.crate_alert',
        'schedule': 60
    },
    'first_action': {
        'task': 'alerting.tasks.first_action',
        'schedule': 60
    },
    'no_confirm_reminder': {
        'task': 'alerting.tasks.no_confirm_reminder',
        'schedule': 86400
    },
    'update_rule': {
        'task': 'prom.tasks.update_rule',
        'schedule': 300
    }
}