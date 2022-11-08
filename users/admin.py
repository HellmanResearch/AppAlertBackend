from django.contrib import admin


from . import models as l_models
from devops_django import models as dd_models


@admin.register(l_models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.User)
    exclude = ("id", )
    list_per_page = 10
