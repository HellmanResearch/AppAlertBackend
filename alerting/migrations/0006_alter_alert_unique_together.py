# Generated by Django 4.1.2 on 2022-11-22 09:12

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('alerting', '0005_auto_20221021_0235'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='alert',
            unique_together={('user', 'prom_alert_id')},
        ),
    ]