
from . import models as l_models
from . import serializers as l_serializers

from rest_framework import exceptions
from rest_framework import viewsets
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings

from ssv import tasks as ssv_tasks


class TestUser(viewsets.ModelViewSet):
    queryset = l_models.User.objects.all()
    serializer_class = l_serializers.TestUser

    permission_classes = []

    def list(self, request, *args, **kwargs):
        html_message = "<h1>HHHHHHH</h1>"
        # send_mail("AAA", "mmm", from_email=settings.EMAIL_HOST_USER, recipient_list=["mingmingtang@aliyun.com"],
        #           html_message=html_message)
        # ssv_tasks.sync_operator()
        # ssv_tasks.sync_operator()
        if settings.ENV != "LOCAL":
            raise exceptions.ParseError("The interface can only be called in local environment")
        function_name = request.query_params.get("function_name")
        function = getattr(ssv_tasks, function_name)
        function()
        return Response({})

    def create(self, request, *args, **kwargs):
        html_message = "<h1>HHHHHHH</h1>"
        # send_mail("AAA", "mmm", from_email=settings.EMAIL_HOST_USER, recipient_list=["mingmingtang@aliyun.com"],
        #           html_message=html_message)
        ssv_tasks.process_decided_to_operator_decided()
        return Response({})
