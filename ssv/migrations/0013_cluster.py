# Generated by Django 4.1.2 on 2023-04-19 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssv', '0012_alter_operatorperformancerecord_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.CharField(max_length=66, primary_key=True, serialize=False)),
                ('owner', models.CharField(max_length=42)),
                ('operator_ids', models.CharField(max_length=50)),
                ('balance_human', models.FloatField(default=0.0)),
                ('validator_count', models.IntegerField(default=1)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
