from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as l_models
from . import serializers as l_serializers


class Account(viewsets.ReadOnlyModelViewSet):

    serializer_class = l_serializers.Account
    queryset = l_models.Account.objects.all()

    @action(methods=["get"], detail=False, url_path="account-balance-choices")
    def get_account_balance_choices(self, request, *args, **kwargs):
        account_qs = self.queryset.all()
        choices = [[item.public_key, f"{item.public_key} {item.ssv_balance_human} SSV"] for item in account_qs]
        return Response(choices)


class Operator(viewsets.ReadOnlyModelViewSet):
    serializer_class = l_serializers.Operator
    queryset = l_models.Operator.objects.all()

    @action(methods=["get"], detail=False, url_path="operator-choices")
    def get_operator_choices(self, request, *args, **kwargs):
        operator_qs = self.queryset.all()
        choices = [[item.id, f"{item.id} | {item.name}"] for item in operator_qs]
        return Response(choices)
