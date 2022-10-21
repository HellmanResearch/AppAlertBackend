
import logging

from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model


from web3 import Account
from eth_account.messages import encode_defunct


from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import decorators
from rest_framework import exceptions
from rest_framework.decorators import action

from devops_django import decorators as dd_decorators

from . import models as l_models
from . import serializers as l_serializers
from . import objects as l_objects
from .objects import user as l_object_user

User = get_user_model()

logger = logging.getLogger("user")


class User(viewsets.GenericViewSet):
    serializer_class = l_serializers.User
    queryset = l_models.User.objects.all()

    @action(methods=["get"], detail=False, url_path="signature-content", permission_classes=[])
    @dd_decorators.parameter("public_key", str, False, True, default=None)
    def get_signature_content(self, request, public_key, *args, **kwargs):
        # public_key = self.request.query_params.get("public_key")
        user, _ = l_object_user.UserObject.get_or_create(public_key)
        data = {
            "signature_content": user.signature_content
        }
        return Response(data)

    @action(methods=["get"], detail=False, url_path="login-signature", permission_classes=[])
    @dd_decorators.parameter("public_key", str, False, True, default=None)
    @dd_decorators.parameter("signature", str, False, True, default=None)
    def login_signature(self, request, public_key, signature, *args, **kwargs):
        user, is_new = l_object_user.UserObject.get_or_create(public_key)
        if is_new is True:
            raise exceptions.ParseError("The user doesn't exist, please get signature content first to create")

        try:
            message = encode_defunct(text=user.signature_content)
            recovered_address = Account.recover_message(message, signature=signature)
        except Exception as exc:
            logger.info(f"recover_message error: {exc}")
            raise exceptions.ParseError("Signature is incorrect")

        if recovered_address.lower() == public_key.lower():
            login(request, user)
            l_object_user.UserObject(user).reset_signature_content()
            serializer = l_serializers.User(user)
            # data = {
            #     "result": "login successful"
            # }
            return Response(serializer.data)
        else:
            raise exceptions.ParseError("signature is incorrect")
