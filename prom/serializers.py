
from rest_framework import serializers

from . import models as l_models
from .metrics_rules.field import NameFiledMap


def gen_fields_attr_serializer_cls(fields_attr) -> serializers.Serializer:

    # for filed_attr in filed_attr_list:
    #     field_cls = NameFiledMap.get(filed_attr["type"])
    #     if field_cls is None:
    #         raise Exception('filed_attr["type"] not support')
    #     field = field_cls(**filed_attr)
    #     field_dict[filed_attr["key"]] = field
    # serializer_cls = type("DynamicSerializer", (serializers.Serializer,), field_dict)
    # return serializer_cls

    for key, filed_attr in fields_attr.items():
        serializer = NameFiledMap[filed_attr["type"]].ArgsSerializer(data=fields_attr)
        serializer.is_valid(raise_exception=True)


class Metric(serializers.ModelSerializer):

    def validate_fields_attr(self, value):
        for key, filed_attr in value.items():
            serializer = NameFiledMap[filed_attr["type"]].ArgsSerializer(data=filed_attr)
            serializer.is_valid(raise_exception=True)
        # serializer_class = gen_fields_attr_serializer_cls(value)
        # serializer = serializer_class(data=value)
        # serializer.is_valid(raise_exception=True)
        # return serializer.validated_data
        return value

    class Meta:
        model = l_models.Metric
        fields = "__all__"


class MetricGroup(serializers.ModelSerializer):
    metrics = Metric(many=True, read_only=True)

    class Meta:
        model = l_models.MetricGroup
        fields = "__all__"


class Rule(serializers.ModelSerializer):

    class Meta:
        model = l_models.Rule
        fields = "__all__"


class PromAlert(serializers.ModelSerializer):

    class Meta:
        model = l_models.Alert
        fields = "__all__"
