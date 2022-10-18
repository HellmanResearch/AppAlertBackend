from django.db import models


class Account(models.Model):
    public_key = models.CharField(max_length=42, primary_key=True)
    ssv_balance_human = models.FloatField()

    def __str__(self):
        return self.public_key

    class Meta:
        db_table = "account"


class Operator(models.Model):
    name = models.CharField(max_length=50)
    account_public_key = models.CharField(max_length=42)
    status = models.CharField(max_length=10)
    validator_count = models.IntegerField()
    fee_human = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "operator"

