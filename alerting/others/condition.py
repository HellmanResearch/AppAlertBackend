
from rest_framework import serializers

from prom.metrics_rules.field import NameFiledMap


class ConditionSerializer(serializers.JSONField):

    def __init__(self, filed_attr_list: list[dict], **kwargs):
        super().__init__(**kwargs)
        self.c_filed_attr_list = filed_attr_list

    def c_get_serializer_cls(self):
        field_dict = {}
        for filed_attr in self.c_filed_attr_list:
            field_cls = NameFiledMap.get(filed_attr["type"])
            if field_cls is None:
                raise Exception('filed_attr["type"] not support')
            field = field_cls(**filed_attr)
            field_dict[filed_attr["key"]] = field
        serializer_cls = type("DynamicSerializer", (serializers.Serializer,), field_dict)
        return serializer_cls

    def validate(self, attr):
        serializer_cls = self.c_get_serializer_cls()
        serializer = serializer_cls(data=attr)
        serializer.is_valid(raise_exception=True)
