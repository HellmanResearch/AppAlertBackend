import logging

from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response


from . import models as l_models
from . import serializers as l_serializers

from .objects.subscribe import SubscribeObject

from prom.objects.alert import AlertObject
from prom.objects.rule import RuleObject

User = get_user_model()


logger = logging.getLogger(__name__)


class Subscribe(viewsets.ModelViewSet):
    queryset = l_models.Subscribe.objects.all()
    serializer_class = l_serializers.Subscribe

    # @transaction.atomic
    # def create(self, request, *args, **kwargs):
    #     response = super().create(request, *args, **kwargs)
    #     serializer = self.get_serializer()
    #     metric = serializer.validated_data["metric"]
    #     error_info, expr = SubscribeObject(serializer.instance).render_template_to_expr()
    #     if error_info:
    #         logger.error(f"rule render error: {error_info}")
    #         raise Exception("rule render error")
    #     RuleObject.get_or_crate(metric, expr)
    #     return response


class Alert(viewsets.ReadOnlyModelViewSet):
    queryset = l_models.Alert.objects.all()
    serializer_class = l_serializers.Alert

    # def create(self, request, *args, **kwargs):
    #     logger.info("received a alert: ", request.data)
    #     # serializer = self.get_serializer(data=request.data)
    #     # serializer.is_valid(raise_exception=True)
    #     # self.perform_create(serializer)
    #     # headers = self.get_success_headers(serializer.data)
    #     return Response({}, 200)


