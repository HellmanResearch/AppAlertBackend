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
    id = models.BigIntegerField(primary_key=True)
    missed = models.BooleanField()
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
