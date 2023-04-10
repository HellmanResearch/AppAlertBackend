from django.db import models

# Create your models here.


class Decided(models.Model):
    # id = models.BigIntegerField(primary_key=True)
    validator_public_key = models.CharField(max_length=110, db_index=True)
    height = models.IntegerField(db_index=True)
    # round = models.IntegerField()
    signers = models.CharField(max_length=80)
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = (("validator_public_key", "height"), )


class OperatorDecided(models.Model):
    decided_id = models.IntegerField(db_index=True)
    operator_id = models.IntegerField()
    height = models.IntegerField()
    missed = models.BooleanField(db_index=True)
    time = models.DateTimeField(db_index=True)


class Account(models.Model):
    public_key = models.CharField(max_length=42, primary_key=True)
    ssv_balance_human = models.FloatField(default=0.0)

    def __str__(self):
        return self.public_key

#
# class Operator(models.Model):
#     name = models.CharField(max_length=50)
#     account_public_key = models.CharField(max_length=42)
#     status = models.CharField(max_length=10)
#     validator_count = models.IntegerField()
#     fee_human = models.FloatField()
#     performance_1day = models.FloatField()
#
#     def __str__(self):
#         return self.name


class OperatorValidator(models.Model):
    operator_id = models.IntegerField()
    validator_public_key = models.CharField(max_length=110)

    class Meta:
        unique_together = (("operator_id", "validator_public_key"), )


class Performance(models.Model):
    operator_id = models.IntegerField()
    performance = models.FloatField()
    timestamp = models.IntegerField()


class Tag(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=100)
