# chat/webhook_views.py

import os
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework.views import APIView

from .models import Customer, ChatMessage
from .utils import send_whatsapp, send_instagram

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")

class MetaWebhook(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        mode      = request.GET.get("hub.mode")
        token     = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponseForbidden("Invalid verification token")

    def post(self, request, *args, **kwargs):
        payload = request.data

        # WhatsApp messages
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                val = change.get("value", {})
                for msg in val.get("messages", []):
                    sender = msg.get("from")
                    text   = msg.get("text", {}).get("body", "")
                    customer, _ = Customer.objects.get_or_create(
                        platform="whatsapp", user_id=sender
                    )
                    ChatMessage.objects.create(customer=customer, inbound=True, text=text)
                    reply = "Thanks—got your WhatsApp message!"
                    ChatMessage.objects.create(customer=customer, inbound=False, text=reply)
                    send_whatsapp(sender, reply)

        # Instagram DMs
        for entry in payload.get("entry", []):
            for dm_event in entry.get("messaging", []):
                msg = dm_event.get("message")
                if not msg:
                    continue
                sender = dm_event["sender"]["id"]
                text   = msg.get("text", "")
                customer, _ = Customer.objects.get_or_create(
                    platform="instagram", user_id=sender
                )
                ChatMessage.objects.create(customer=customer, inbound=True, text=text)
                reply = "Thanks—got your Instagram DM!"
                ChatMessage.objects.create(customer=customer, inbound=False, text=reply)
                send_instagram(sender, reply)

        return HttpResponse(status=200)
