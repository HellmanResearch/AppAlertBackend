

from enum import Enum

from rest_framework import serializers


class FiledType(Enum):
    INPUT = "input"
    CHOICE = "choice"
    SELECT = "select"

    @classmethod
    def get_choices(cls):
        choices = list(((filed.name, filed.value) for filed in cls._member_map_.values()))
        return choices


class Field(serializers.Field):

    class BaseArgsSerializer(serializers.Serializer):
        key = serializers.CharField(required=True, max_length=20)
        display = serializers.CharField(required=True, max_length=20)
        type = serializers.ChoiceField(required=True, choices=FiledType.get_choices())
        description = serializers.CharField(required=True, max_length=100)

    def __init__(self, key: str, display: str, description: str, type: FiledType):
        self.key = key
        self.display = display
        self.type = type
        self.description = description

    def check_args(self, args: dict):
        raise NotImplementedError("function check_args")

    def generate_serializer_field(self, *args, **kwargs):
        raise NotImplementedError("function generate_serializer_field")

    @classmethod
    def check_args(cls, args: dict) -> (bool, dict):
        serializer = cls.check_args_serialize(data=args)
        if serializer.is_valid(raise_exception=False) is True:
            return True, ""
        return False, serializer.errors


class InputField(Field):

    class ArgsSerializer(Field.BaseArgsSerializer):
        pass

    def __init__(self, key: str, display: str, description: str):
        super().__init__(key=key, display=display, description=description, type=FiledType.INPUT)

    def generate_serializer_field(self):
        return serializers.CharField()


class ChoiceField(Field):

    class ArgsSerializer(Field.BaseArgsSerializer):
        multiple = serializers.BooleanField()
        choices = serializers.ListSerializer(child=serializers.ListSerializer(child=serializers.CharField()))
        is_remote = serializers.BooleanField(required=True)
        remote_url = serializers.CharField(required=True)

    def __init__(self, key: str, display: str, description: str, multiple: bool, choices, is_remote: bool, remote_url: str):
        super().__init__(key=key, display=display, description=description, type=FiledType.CHOICE)
        self.multiple = multiple
        self.choices = choices
        self.is_remote = is_remote
        self.remote_url = remote_url

    # @classmethod
    # def check_args(cls, args: dict):
    #     args_serializer = cls.ArgsSerializer(data=args)
    #     args_serializer.is_valid(raise_exception=True)

    def generate_serializer_field(self):
        if self.is_remote is True:
            if self.multiple:
                return serializers.ListSerializer(child=serializers.CharField(required=True))
            else:
                return serializers.CharField()
        else:
            if self.multiple:
                return serializers.MultipleChoiceField(choices=self.choices)
            else:
                return serializers.ChoiceField(choices=self.choices)


class SelectField(ChoiceField):
    pass
    # class ArgsSerializer(Field.BaseArgsSerializer):
    #     multiple = serializers.BooleanField(required=True)
    #     choices = serializers.ListSerializer(child=serializers.ListSerializer(child=serializers.CharField()))
    #     is_remote = serializers.BooleanField(required=True)
    #     remote_url = serializers.CharField(required=False)
    #
    # def generate_serializer_field(self):
    #     if self.multiple:
    #         return serializers.MultipleChoiceField(choices=self.choices)
    #     else:
    #         return serializers.ChoiceField(choices=self.choices)


# class SelectField(Field):
#
#     def __init__(self, key: str, display: str, description: str, multiple: bool, choices_url: str, choices_filed=str):
#         super().__init__(key=key, display=display, description=description, type=FiledType.CHOICE)
#         self.multiple = multiple
#         self.choices_url = choices_url
#         self.choices_field = choices_filed


NameFiledMap = {
    "INPUT": InputField,
    "CHOICE": ChoiceField,
    "SELECT": SelectField,
}
