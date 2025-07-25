# chat/webhook_views.py

import os
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework.views import APIView

from .models import Customer, ChatMessage
from .utils import send_whatsapp, send_instagram
from .chatbot import generate_reply, get_quick_replies

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
        print("[DEBUG] Webhook POST payload:", payload)

        # 1) Instagram test payload using 'field'/'value' format
        if payload.get("field") == "messages":
            val = payload.get("value", {})
            sender_id = val.get("sender", {}).get("id")
            text = val.get("message", {}).get("text", "")
            print(f"[DEBUG] Instagram test message from {sender_id!r}: {text!r}")

            customer, _ = Customer.objects.get_or_create(
                platform="instagram", user_id=sender_id
            )
            ChatMessage.objects.create(customer=customer, inbound=True, text=text)

            reply = "Thanks—got your Instagram DM!"
            print(f"[DEBUG] Replying to Instagram {sender_id!r} with: {reply!r}")
            ChatMessage.objects.create(customer=customer, inbound=False, text=reply)

            try:
                resp = send_instagram(sender_id, reply)
                print(f"[DEBUG] send_instagram returned: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"[ERROR] send_instagram exception: {e}")

            return HttpResponse(status=200)

        # 2) Handle WhatsApp messages (entry -> changes -> messages)
        # 2) Handle WhatsApp messages (entry -> changes -> messages)
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                val = change.get("value", {})
                for msg in val.get("messages", []):
                    sender_id = msg.get("from")
                    msg_type  = msg.get("type")

                    # ——— 1) Button replies (interactive postback) ———
                    if msg_type == "interactive" and msg.get("interactive", {}).get("type") == "button_reply":
                        button_id = msg["interactive"]["button_reply"]["id"]
                        print(f"[DEBUG] Button reply from {sender_id!r}: {button_id!r}")

                        customer, _ = Customer.objects.get_or_create(
                            platform="whatsapp", user_id=sender_id
                        )
                        ChatMessage.objects.create(
                            customer=customer, inbound=True, text=f"<button:{button_id}>"
                        )

                        # Use the same generate_reply to map "menu", "hours", etc.
                        reply = generate_reply(button_id)
                        print(f"[DEBUG] Replying to WhatsApp {sender_id!r} with (button): {reply!r}")
                        ChatMessage.objects.create(
                            customer=customer, inbound=False, text=reply
                        )

                        buttons = get_quick_replies()
                        resp = send_whatsapp(sender_id, reply, quick_replies=buttons)
                        print(f"[DEBUG] send_whatsapp returned: {resp.status_code} {resp.text}")

                        continue  # skip the text‐message branch

                    # ——— 2) Plain text messages ———
                    if msg_type == "text":
                        text = msg.get("text", {}).get("body", "")
                        print(f"[DEBUG] WhatsApp message from {sender_id!r}: {text!r}")

                        customer, _ = Customer.objects.get_or_create(
                            platform="whatsapp", user_id=sender_id
                        )
                        ChatMessage.objects.create(
                            customer=customer, inbound=True, text=text
                        )

                        reply = generate_reply(text)
                        print(f"[DEBUG] Replying to WhatsApp {sender_id!r} with: {reply!r}")
                        ChatMessage.objects.create(
                            customer=customer, inbound=False, text=reply
                        )

                        buttons = get_quick_replies()
                        resp = send_whatsapp(sender_id, reply, quick_replies=buttons)
                        print(f"[DEBUG] send_whatsapp returned: {resp.status_code} {resp.text}")


                # 3) Handle Instagram production payload (entry -> messaging)
                for entry in payload.get("entry", []):
                    for event in entry.get("messaging", []):
                        msg = event.get("message")
                        if not msg or "text" not in msg:
                            continue
                        sender_id = event.get("sender", {}).get("id")
                        text      = msg.get("text", "")
                        print(f"[DEBUG] Instagram prod message from {sender_id!r}: {text!r}")

                        customer, _ = Customer.objects.get_or_create(
                            platform="instagram", user_id=sender_id
                        )
                        ChatMessage.objects.create(customer=customer, inbound=True, text=text)

                        reply = "Thanks—got your Instagram DM!"
                        print(f"[DEBUG] Replying to Instagram {sender_id!r} with: {reply!r}")
                        ChatMessage.objects.create(customer=customer, inbound=False, text=reply)

                        try:
                            resp = send_instagram(sender_id, reply)
                            print(f"[DEBUG] send_instagram returned: {resp.status_code} {resp.text}")
                        except Exception as e:
                            print(f"[ERROR] send_instagram exception: {e}")

                # Acknowledge receipt
                return HttpResponse(status=200)
