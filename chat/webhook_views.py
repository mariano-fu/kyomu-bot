# chat/webhook_views.py

import os
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework.views import APIView

from .models import Customer, ChatMessage
from .utils import send_whatsapp, send_instagram

# Keep your verify token secret via environment variable
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")

class MetaWebhook(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        mode      = request.GET.get("hub.mode")
        token     = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        # Verification handshake
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponseForbidden("Invalid verification token")

    def post(self, request, *args, **kwargs):
        payload = request.data

        # 1) Instagram test payload using 'field'/'value' format
        if payload.get("field") == "messages":
            val = payload.get("value", {})
            sender_id = val.get("sender", {}).get("id")
            text = val.get("message", {}).get("text", "")

            customer, _ = Customer.objects.get_or_create(
                platform="instagram", user_id=sender_id
            )
            # Persist inbound message
            ChatMessage.objects.create(
                customer=customer, inbound=True, text=text
            )
            # Send a reply
            reply = "Thanks—got your Instagram DM!"
            ChatMessage.objects.create(
                customer=customer, inbound=False, text=reply
            )
            send_instagram(sender_id, reply)
            return HttpResponse(status=200)

        # 2) Handle WhatsApp messages (entry -> changes -> messages)
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                val = change.get("value", {})
                for msg in val.get("messages", []):
                    sender_id = msg.get("from")
                    text      = msg.get("text", {}).get("body", "")

                    customer, _ = Customer.objects.get_or_create(
                        platform="whatsapp", user_id=sender_id
                    )
                    ChatMessage.objects.create(
                        customer=customer, inbound=True, text=text
                    )

                    reply = "Thanks—got your WhatsApp message!"
                    ChatMessage.objects.create(
                        customer=customer, inbound=False, text=reply
                    )
                    send_whatsapp(sender_id, reply)

        # 3) Handle Instagram production payload (entry -> messaging)
        for entry in payload.get("entry", []):
            for event in entry.get("messaging", []):
                msg = event.get("message")
                if not msg or "text" not in msg:
                    continue
                sender_id = event.get("sender", {}).get("id")
                text      = msg.get("text", "")

                customer, _ = Customer.objects.get_or_create(
                    platform="instagram", user_id=sender_id
                )
                ChatMessage.objects.create(
                    customer=customer, inbound=True, text=text
                )

                reply = "Thanks—got your Instagram DM!"
                ChatMessage.objects.create(
                    customer=customer, inbound=False, text=reply
                )
                send_instagram(sender_id, reply)

        # Acknowledge receipt
        return HttpResponse(status=200)