from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "username", "phone", "distributor", "created_at"]
    search_fields = ["full_name", "username", "phone"]
    readonly_fields = ["created_at"]