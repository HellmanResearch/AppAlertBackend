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
    address = models.CharField(max_length=42, primary_key=True)
    ssv_balance_human = models.FloatField(default=0.0)

    def __str__(self):
        return self.address


class Operator(models.Model):

    # RUN_STATUS = (
    #     ("active", "active"),
    #     ("inactive", "inactive"),
    # )

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    owner_address = models.CharField(max_length=42, null=True, blank=True)
    active = models.BooleanField(default=False)
    # run_status = models.CharField(choices=RUN_STATUS, default="inactive", db_index=True)
    validator_count = models.IntegerField(default=0)
    fee_human = models.FloatField(default=0)
    snapshot_index = models.BigIntegerField(default=0)
    performance_1day = models.FloatField(default=0)
    performance_1month = models.FloatField(default=0)

    def __str__(self):
        return self.name


class Validator(models.Model):
    public_key = models.CharField(max_length=110, unique=True)
    owner_address = models.CharField(max_length=42, null=True, blank=True)
    active = models.BooleanField(default=False)

    operators = models.ManyToManyField(to=Operator)

    def __str__(self):
        return self.public_key


class OperatorValidator(models.Model):
    operator_id = models.IntegerField()
    validator_public_key = models.CharField(max_length=110)

    class Meta:
        unique_together = (("operator_id", "validator_public_key"), )


# class Performance(models.Model):
#     operator_id = models.IntegerField()
#     performance = models.FloatField()
#     timestamp = models.IntegerField()


class Tag(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=100)


class OperatorPerformanceRecord(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, db_index=True)
    performance = models.FloatField()
    time = models.DateTimeField(auto_now_add=True, db_index=True)


class Cluster(models.Model):
    id = models.CharField(max_length=66, primary_key=True)
    owner = models.CharField(max_length=42)
    operator_ids = models.CharField(max_length=50)
    balance = models.CharField(max_length=80, default="0")
    balance_human = models.FloatField(default=0.0)
    validator_count = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    est_days = models.IntegerField(default=0)
    liquidated = models.BooleanField(default=False)
    last_sync_block_number = models.IntegerField(default=0)
    index = models.BigIntegerField(default=0)
    network_fee_index = models.BigIntegerField(default=0)

    class Meta:
        unique_together = (("owner", "operator_ids"), )


