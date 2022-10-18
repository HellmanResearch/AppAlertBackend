
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    public_key = models.CharField(max_length=100, unique=True)
    signature_content = models.CharField(max_length=100)
    max_subscribe = models.IntegerField(default=10)

    def __str__(self):
        return self.public_key
