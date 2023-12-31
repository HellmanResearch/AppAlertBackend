import logging

from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.signing import Signer
from django.conf import settings

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import pagination
from rest_framework.decorators import action
from rest_framework import exceptions

from devops_django import permissions as dd_permissions

from . import models as l_models
from . import serializers as l_serializers
from . import tasks as l_tasks
from .others.send import send as l_send

from .objects.subscribe import SubscribeObject

from prom.objects.alert import AlertObject
from prom.objects.rule import RuleObject

User = get_user_model()

logger = logging.getLogger(__name__)


class TestTask(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        if settings.ENV != "LOCAL":
            raise exceptions.ParseError('settings.ENV != "LOCAL"')
        function_name = request.data["function_name"]
        kwargs = request.data["kwargs"]
        function = getattr(l_tasks, function_name)
        function(**kwargs)
        data = {
            "results": "ok"
        }
        return Response(data)


class Subscribe(viewsets.ModelViewSet):
    queryset = l_models.Subscribe.objects.all()
    serializer_class = l_serializers.Subscribe

    permission_classes = [permissions.IsAuthenticated,
                          dd_permissions.generate_user_obj_perm_class(user_filed="user", safe_methods=["OPTIONS"])]

    filter_fields = ("rule", "metric", "notification_type")
    ordering_fields = ("id", "crate_time")

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        count = self.get_queryset().count()
        if count >= self.request.user.max_subscribe:
            raise exceptions.ParseError(f"Exceeded subscription limit")
        instance = serializer.save(user=self.request.user)
        l_tasks.new_subscribe_check_triggerd.delay(instance.id)

    def perform_update(self, serializer):
        instance = serializer.save(user=self.request.user)
        l_tasks.new_subscribe_check_triggerd.delay(instance.id)

    @action(methods=["post"], detail=False, url_path="action-test")
    def c_test_send(self, request, *args, **kwargs):
        serializer = l_serializers.ActionTest(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            l_send(serializer.validated_data["notification_type"],
                   serializer.validated_data["notification_address"],
                   0,
                   "Send Test",
                   description="XXXX of XXX is lower than XXX !",
                   user_name="0x000000000000000000000000000000000000000")
        except Exception as exc:
            raise exceptions.ParseError(f"send failed: {exc}")
        return Response({})


class Alert(viewsets.ReadOnlyModelViewSet):
    queryset = l_models.Alert.objects.all()
    serializer_class = l_serializers.Alert

    filter_fields = ("confirmed",)
    ordering_fields = ("id", "crate_time")

    permission_classes = [permissions.IsAuthenticated,
                          dd_permissions.generate_user_obj_perm_class(user_filed="user", safe_methods=["OPTIONS"])]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    @action(methods=["post"], detail=True, url_path="confirm")
    def c_confirm(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.confirmed = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=["post"], detail=True, permission_classes=[], url_path="confirm-via-sign")
    def c_confirm_via_sign(self, request, *args, **kwargs):
        # instance = super().get_object()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        id = kwargs[lookup_url_kwarg]
        instance = get_object_or_404(self.queryset, **{self.lookup_field: id})

        serializer = l_serializers.ConfirmViaSign(data=request.data)
        serializer.is_valid(raise_exception=True)
        sign = serializer.validated_data["sign"]
        signer = Signer()
        try:
            alert_id_str = signer.unsign(sign)
        except Exception as exc:
            raise exceptions.ParseError("sign error")
        if alert_id_str != str(instance.id):
            raise exceptions.ParseError("id not match alert and unsigned")

        instance.confirmed = True
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=["post"], detail=False, url_path="confirm-all")
    def c_confirm_all(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(confirmed=False)
        count = qs.count()
        qs.update(confirmed=True)
        data = {
            "count": count
        }
        return Response(data)
