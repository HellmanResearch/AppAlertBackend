# Generated by Django 3.2.15 on 2022-10-18 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='max_subscribe',
            field=models.IntegerField(default=10),
        ),
    ]
