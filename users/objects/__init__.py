
import uuid
from .. import models as l_models


class UserObject:

    def __init__(self, user: l_models.User):
        self.user = user

    @staticmethod
    def generate_signature_content():
        return uuid.uuid4().hex

    @classmethod
    def get_or_create(cls, public_key: str) -> (l_models.User, bool):
        try:
            user = l_models.User.objects.get(public_key=public_key)
            return user, False
        except l_models.User.DoesNotExist:
            signature_content = cls.generate_signature_content()
            user = l_models.User()
            user.signature_content = signature_content
            user.public_key = public_key
            user.save()
            return user, True

    def reset_signature_content(self):
        signature_content = self.generate_signature_content()
        self.user.signature_content = signature_content
        self.user.save()


