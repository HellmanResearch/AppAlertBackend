# Generated by Django 4.1.2 on 2023-04-13 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssv', '0011_remove_validator_performance_1day_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operatorperformancerecord',
            name='time',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
