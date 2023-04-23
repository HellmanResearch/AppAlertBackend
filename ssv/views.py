from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models as l_models
from . import serializers as l_serializers


class Operator(viewsets.ReadOnlyModelViewSet):
    serializer_class = l_serializers.Operator
    queryset = l_models.Operator.objects.all()

    permission_classes = []

    filter_fields = [""]

    @action(methods=["get"], detail=False, url_path="operator-choices", permission_classes=[])
    def get_operator_choices(self, request, *args, **kwargs):
        operator_qs = self.queryset.all()
        choices = [[item.id, f"{item.id}|{item.name}"] for item in operator_qs]
        return Response(choices)


class Validator(viewsets.ReadOnlyModelViewSet):
    serializer_class = l_serializers.Validator
    queryset = l_models.Validator.objects.all()

    permission_classes = []

    filter_fields = [""]

    @action(methods=["get"], detail=False, url_path="validator-choices", permission_classes=[])
    def c_get_validator_choices(self, request, *args, **kwargs):
        validator_qs = self.queryset.all()
        choices = [[item.public_key, item.public_key] for item in validator_qs]
        return Response(choices)


class Cluster(viewsets.ReadOnlyModelViewSet):
    serializer_class = l_serializers.Cluster
    queryset = l_models.Cluster.objects.all()

    permission_classes = []

    filter_fields = [""]

    @action(methods=["get"], detail=False, url_path="cluster-choices", permission_classes=[])
    def c_get_cluster_choices(self, request, *args, **kwargs):
        cluster_qs = self.queryset.all()
        choices = [[item.id, f"{item.id}|{item.owner}"] for item in cluster_qs]
        return Response(choices)
