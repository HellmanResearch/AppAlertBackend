# Generated by Django 4.1.2 on 2023-04-10 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssv', '0002_alter_decided_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decided',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
