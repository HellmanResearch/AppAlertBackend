
from rest_framework import serializers

from . import models as l_models


class User(serializers.ModelSerializer):

    class Meta:
        model = l_models.User
        fields = "__all__"
