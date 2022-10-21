import datetime
import json
import logging

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from . import models as l_models
from . import serializers as l_serializers
from rest_framework import viewsets

logger = logging.getLogger(__name__)


class MetricGroup(viewsets.ReadOnlyModelViewSet):
    queryset = l_models.MetricGroup.objects.all()
    serializer_class = l_serializers.MetricGroup

    permission_classes = []


class Metric(viewsets.ModelViewSet):
    queryset = l_models.Metric.objects.all()
    serializer_class = l_serializers.Metric

    permission_classes = []


# class Rule(viewsets.GenericViewSet):
#     pass


class Alert(viewsets.GenericViewSet):
    queryset = l_models.Alert.objects.all()
    serializer_class = l_serializers.PromAlert

    def create(self, request, *args, **kwargs):
        body_content = json.dumps(request.data)
        logger.info("received a alert body_content: ", body_content)
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
                datetime_str = alert["startsAt"].lstrip("Z")
                start_at = datetime.datetime.fromisoformat(datetime_str)
                l_models.Alert.objects.create(rule=rule, start_at=start_at)
            except Exception as exc:
                logger.error(f"parse alert to save error alert: {json.dumps(alert)} exc: {exc}")
        return Response({}, 200)
