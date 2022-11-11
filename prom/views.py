import datetime
import json
import logging
import time

import jinja2
import requests

from django.conf import settings

from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.decorators import action

from prometheus_client import Gauge

from . import models as l_models
from . import serializers as l_serializers
from rest_framework import viewsets
from . import tasks as l_tasks
from alerting import serializers as alerting_serializers

logger = logging.getLogger(__name__)
count_error_parse_alert = Gauge(name="count_error_parse_alert", documentation="")


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


class MetricGroup(viewsets.ReadOnlyModelViewSet):
    queryset = l_models.MetricGroup.objects.all()
    serializer_class = l_serializers.MetricGroup

    permission_classes = []

    ordering_fields = ("id", "crate_time")

    class Meta:
        pass


class Metric(viewsets.ModelViewSet):
    queryset = l_models.Metric.objects.all()
    serializer_class = l_serializers.Metric

    permission_classes = []

    filter_fields = ("group",)
    ordering_fields = ("id", "crate_time")

    class Meta:
        pass

    @action(methods=["post"], detail=True, url_path="history")
    def c_history(self, request, *args, **kwargs):
        object = self.get_object()
        cls = alerting_serializers.Subscribe.c_get_conditions_serializer_cls(object.query_attr)
        serializer = cls(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = jinja2.Template(object.query_template)
        try:
            query = template.render(query=serializer.validated_data)
        except Exception as exc:
            raise exceptions.ParseError(f"render template error: {exc}")
        step = 86400
        end = time.time()
        start = end - (step * 30)
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step
        }
        url = f"{settings.PROM_BASE_URL}/api/v1/query_range"
        try:
            response = requests.get(url, params=params, timeout=10)
        except Exception as exc:
            logger.error(f"get data error from prometheus exc: {exc}")
            raise exceptions.ParseError("get data error")
        if response.status_code != 200:
            logger.error(f"status_code: {response.status_code} body: {response.text}")
            raise exceptions.ParseError("get data error")
        data = response.json()
        if len(data["data"]["result"]) != 1:
            raise exceptions.ParseError("data error")
        return Response(data["data"]["result"][0]["values"])

        # instance = self.get_object()
        # instance.confirmed = True
        # instance.save()
        # serializer = self.get_serializer(instance)
        # return Response(serializer.data)


# class Rule(viewsets.GenericViewSet):
#     pass


class Alert(viewsets.GenericViewSet):
    queryset = l_models.Alert.objects.all()
    serializer_class = l_serializers.PromAlert

    permission_classes = []

    def create(self, request, *args, **kwargs):
        if request.META.get("REMOTE_ADDR") != settings.PROM_ADDR:
            raise exceptions.PermissionDenied()
        body_content = json.dumps(request.data)
        logger.info(f"received a alert body_content: {body_content}")
        for alert in request.data["alerts"]:
            try:
                if alert["status"] != "firing":
                    continue
                rule_id = int(alert["labels"]["alertname"])
                try:
                    rule = l_models.Rule.objects.get(id=rule_id)
                except l_models.Rule.DoesNotExist:
                    logger.warning(f"unknown alertname: {rule_id}")
                    continue
                datetime_str = alert["startsAt"].rstrip("Z")
                start_at = datetime.datetime.fromisoformat(datetime_str)
                l_models.Alert.objects.create(rule=rule, start_at=start_at)
            except Exception as exc:
                count_error_parse_alert.inc()
                logger.error(f"parse alert to save error alert: {json.dumps(alert)} exc: {exc}")
        return Response({}, 200)

    class Meta:
        pass
