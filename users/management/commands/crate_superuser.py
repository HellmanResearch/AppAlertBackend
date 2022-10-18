

from django.core.management.base import BaseCommand
from django.core import signing
from django.db.utils import IntegrityError

from users.models import User


class Command(BaseCommand):
    help = 'create a superuser'

    def handle(self, *args, **options):
        user = User()
        user.username = input("username:")
        user.set_password(input("password:"))
        user.public_key = user.username
        user.signature_content = "abc"
        user.max_subscribe = 10
        user.is_staff = True
        user.is_superuser = True
        try:
            user.save()
        except Exception as exc:
            print(f"failed to crate user, error: {exc}")
            return
        print("create successful")
