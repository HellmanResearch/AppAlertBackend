import logging

from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import pagination
from rest_framework.decorators import action

from devops_django import permissions as dd_permissions

from . import models as l_models
from . import serializers as l_serializers
from . import tasks as l_tasks

from .objects.subscribe import SubscribeObject

from prom.objects.alert import AlertObject
from prom.objects.rule import RuleObject

User = get_user_model()

logger = logging.getLogger(__name__)


class TestTask(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
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
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    # def c_action_test(self, request, *args, **kwargs):
    #     serializer = l_serializers.ActionTest(data=request.data)
    #     serializer.is_valid(raise_exception=True)

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

    filter_fields = ("confirmed", )
    ordering_fields = ("id", "crate_time")

    permission_classes = [permissions.IsAuthenticated,
                          dd_permissions.generate_user_obj_perm_class(user_filed="user", safe_methods=["OPTIONS"])]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    # def create(self, request, *args, **kwargs):
    #     logger.info("received a alert: ", request.data)
    #     # serializer = self.get_serializer(data=request.data)
    #     # serializer.is_valid(raise_exception=True)
    #     # self.perform_create(serializer)
    #     # headers = self.get_success_headers(serializer.data)
    #     return Response({}, 200)

    @action(methods=["post"], detail=True, url_path="confirm")
    def c_confirm(self, request, *args, **kwargs):
        instance = self.get_object()
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
