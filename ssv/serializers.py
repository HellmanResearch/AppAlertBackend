from rest_framework import serializers

from . import models as l_models


class Account(serializers.ModelSerializer):

    class Meta:
        model = l_models.Account
        fields = "__all__"


class Operator(serializers.ModelSerializer):

    class Meta:
        model = l_models.Operator
        fields = "__all__"


class Validator(serializers.ModelSerializer):

    class Meta:
        model = l_models.Validator
        fields = "__all__"

