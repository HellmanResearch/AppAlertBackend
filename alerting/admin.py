from django.contrib import admin


from . import models as l_models
from devops_django import models as dd_models


@admin.register(l_models.Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Subscribe)
    exclude = ("id", )
    list_display_links = ("name",)
    list_per_page = 10


@admin.register(l_models.Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Alert)
    list_display_links = ("id",)
    list_per_page = 10
