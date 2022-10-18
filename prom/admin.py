from django.contrib import admin


from . import models as l_models
from devops_django import models as dd_models


@admin.register(l_models.Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Metric)
    exclude = ("id", )
    list_display_links = ("display",)
    list_per_page = 10


@admin.register(l_models.MetricGroup)
class MetricGroupAdmin(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.MetricGroup)
    list_display_links = ("name",)
    list_per_page = 10


@admin.register(l_models.Alert)
class MetricGroupAdmin(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Alert)
    list_display_links = ("id",)
    list_per_page = 10


@admin.register(l_models.Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Rule)
    list_display_links = ("id",)
    list_per_page = 10
