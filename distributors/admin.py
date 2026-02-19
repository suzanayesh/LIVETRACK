from django.contrib import admin

from .models import Distributor


@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "area", "created_at")
    search_fields = ("name", "area")
    ordering = ("-created_at",)
