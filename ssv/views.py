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
        choices = [[item.id, str(item.id)] for item in operator_qs]
        return Response(choices)
