import datetime
import json
import logging

from django.conf import settings

from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import exceptions

from prometheus_client import Gauge


from . import models as l_models
from . import serializers as l_serializers
from rest_framework import viewsets
from . import tasks as l_tasks

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

    filter_fields = ("group", )
    ordering_fields = ("id", "crate_time")

    class Meta:
        pass


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
