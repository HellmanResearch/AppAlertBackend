from django.contrib import admin

from . import models as l_models
from devops_django import models as dd_models


@admin.register(l_models.Decided)
class Decided(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Decided)
    list_display_links = ("id",)
    list_per_page = 10


@admin.register(l_models.OperatorDecided)
class OperatorDecided(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.OperatorDecided)
    list_display_links = ("id",)
    list_per_page = 10


@admin.register(l_models.Account)
class Account(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Account)
    list_display_links = ("address",)
    list_per_page = 10


@admin.register(l_models.Operator)
class Operator(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Operator)
    list_display_links = ("id",)
    list_per_page = 10


@admin.register(l_models.Validator)
class Validator(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Validator)
    list_display_links = ("id",)
    list_per_page = 10


@admin.register(l_models.Cluster)
class Cluster(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Cluster)
    list_display_links = ("id",)
    list_per_page = 10


@admin.register(l_models.Tag)
class Tag(admin.ModelAdmin):
    list_display = dd_models.get_all_field_name(l_models.Tag)
    list_display_links = ("key",)
    list_per_page = 10
