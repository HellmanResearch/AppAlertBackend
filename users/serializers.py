
from rest_framework import serializers

from . import models


class User(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = "__all__"
