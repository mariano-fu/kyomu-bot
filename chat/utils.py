import os
import requests

# Load tokens from environment
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_TOKEN")

# Helper to send a WhatsApp message via Cloud API
def send_whatsapp(to: str, text: str) -> requests.Response:
    url = f"https://graph.facebook.com/v15.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    return requests.post(url, json=payload, headers=headers)

# Helper to send an Instagram DM via Graph API
def send_instagram(to: str, text: str) -> requests.Response:
    url = "https://graph.facebook.com/v15.0/me/messages"
    headers = {"Authorization": f"Bearer {INSTAGRAM_TOKEN}"}
    payload = {"recipient": {"id": to}, "message": {"text": text}}
    return requests.post(url, json=payload, headers=headers)
