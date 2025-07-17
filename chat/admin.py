from django.contrib import admin
from .models import Customer, ChatMessage

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user_id", "platform")
    list_filter = ("platform",)
    search_fields = ("user_id",)
    ordering = ("user_id",)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("short_text", "customer", "get_platform", "inbound", "timestamp")
    list_filter = ("inbound", "customer__platform")
    search_fields = ("text", "customer__user_id")
    ordering = ("-timestamp",)

    def get_platform(self, obj):
        return obj.customer.platform
    get_platform.short_description = "Platform"

    def short_text(self, obj):
        # Truncate long messages for display
        return obj.text if len(obj.text) <= 50 else f"{obj.text[:47]}..."
    short_text.short_description = "Message"
