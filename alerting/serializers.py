import jinja2

from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers
from rest_framework import exceptions

from .objects.subscribe import SubscribeObject
from prom.metrics_rules.field import NameFiledMap
from . import models as l_models
from prom import models as prom_models

User = get_user_model()


class Subscribe(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    @staticmethod
    def c_get_conditions_serializer_cls(fields_attr):
        field_dict = {}
        for key, filed_attr in fields_attr.items():
            field_cls = NameFiledMap.get(filed_attr["type"])
            if field_cls is None:
                raise Exception('filed_attr["type"] not support')
            filed_attr.pop("type")
            field = field_cls(**filed_attr)
            field_dict[filed_attr["key"]] = field.generate_serializer_field()
        serializer_cls = type("DynamicSerializer", (serializers.Serializer,), field_dict)
        return serializer_cls

    def validate_conditions(self, value):
        metric_id = self.initial_data.get("metric")
        # fields_attr = metric.fields_attr

        if metric_id is None:
            raise exceptions.ValidationError("metric is required")
        try:
            metric = prom_models.Metric.objects.get(id=int(metric_id))
        except Exception as exc:
            raise exceptions.ValidationError(f"get metric from db error: {exc}")
        fields_attr = metric.fields_attr
        # fields_attr = self.validated_data["metric"].fields_attr
        serializer_cls = self.c_get_conditions_serializer_cls(fields_attr)
        serializer = serializer_cls(data=value)
        serializer.is_valid(raise_exception=True)
        return value

    @transaction.atomic
    def save(self, **kwargs):
        metric = self.validated_data["metric"]
        template = jinja2.Template(self.validated_data["metric"].rule_template)
        try:
            expr = template.render(conditions=self.validated_data["conditions"])
        except Exception as exc:
            raise exceptions.ParseError(f"render template error: {exc}")
        rule, _ = prom_models.Rule.objects.get_or_create(metric=metric, expr=expr)
        kwargs["rule"] = rule
        super().save(**kwargs)

    # def validate(self, attrs):
    #     metric = attrs.get("metric")
    #     # fields_attr = metric.fields_attr
    #
    #     if metric is None:
    #         raise exceptions.ValidationError("metric is required")
    #     # try:
    #     #     metric = prom_models.Metric.objects.get(id=int(metric_id))
    #     # except Exception as exc:
    #     #     raise exceptions.ValidationError(f"get metric from db error: {exc}")
    #     fields_attr = metric.fields_attr
    #     # fields_attr = self.validated_data["metric"].fields_attr
    #     serializer_cls = self.c_get_conditions_serializer_cls(fields_attr)
    #     serializer = serializer_cls(data=attrs["conditions"])
    #     serializer.is_valid(raise_exception=True)

    # def validate_conditions(self, value):
    #     fields_attr = self.validated_data["metric"].fields_attr
    #     serializer_cls = self.c_get_conditions_serializer_cls(fields_attr)
    #     serializer = serializer_cls(data=value)
    #     serializer.is_valid(raise_exception=True)

    class Meta:
        model = l_models.Subscribe
        exclude = ("rule",)


class Alert(serializers.ModelSerializer):

    subscribe__name = serializers.CharField(read_only=True, source="subscribe.name")

    class Meta:
        model = l_models.Alert
        fields = "__all__"


class ActionTest(serializers.ModelSerializer):

    class Meta:
        model = l_models.Subscribe
        fields = ["notification_type", "notification_address"]


