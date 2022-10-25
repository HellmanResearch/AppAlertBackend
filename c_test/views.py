
from . import models as l_models
from . import serializers as l_serializers
from rest_framework import viewsets


class User(viewsets.ModelViewSet):
    queryset = l_models.User.objects.all()
    serializer_class = l_serializers.User

    permission_classes = []

