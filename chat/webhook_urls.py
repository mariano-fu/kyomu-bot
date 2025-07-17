# chat/webhook_urls.py
from django.urls import path
from .webhook_views import MetaWebhook

urlpatterns = [
    path("", MetaWebhook.as_view(), name="meta-webhook"),
]
