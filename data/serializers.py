from rest_framework import serializers

from . import models as l_models


class Account(serializers.ModelSerializer):

    class Meta:
        models = l_models.Account
        fields = "__all__"


class Operator(serializers.ModelSerializer):

    class Meta:
        models = l_models.Operator
        fields = "__all__"