import json

from rest_framework import serializers

from .. metrics_rules.field import FiledType, NameFiledMap


class FiledSerializer(serializers.Serializer):
    key = serializers.CharField()
    display = serializers.CharField()
    description = serializers.CharField()
    type = serializers.ChoiceField(choices=FiledType.get_choices())
    args = serializers.DictField()

    def validate_args(self, args):
        cls = NameFiledMap[self.type]
        cls.check_args(args)


class FormSerializer(serializers.Serializer):
    name = serializers.CharField()
    fields = FiledSerializer(many=True)


class Form:

    @classmethod
    def serializer(cls, metadata: str) -> "Form":
        filed_attr_list = json.loads(metadata)
        field_dict = {}
        for filed_attr in filed_attr_list:
            field_cls = NameFiledMap.get(filed_attr["type"])
            if field_cls is None:
                raise Exception('filed_attr["type"] not support')
            field = field_cls(**filed_attr)
            field_dict[filed_attr["key"]] = field
        serializer_cls = type("DynamicSerializer", (serializers.Serializer,), field_dict)
        return serializer_cls


