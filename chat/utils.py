import os
import requests

# Load tokens from environment
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_TOKEN")

# Helper to send a WhatsApp message (supports quick replies)
def send_whatsapp(to: str, text: str, quick_replies=None) -> requests.Response:
    url = f"https://graph.facebook.com/v15.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    if quick_replies:
        # Interactive message with buttons
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {
                    "buttons": quick_replies  # Must be a list of {type, reply: {id, title}}
                }
            }
        }
    else:
        # Simple text message
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }

    return requests.post(url, json=payload, headers=headers)


# Helper to send an Instagram DM (supports quick replies if needed)
def send_instagram(to: str, text: str, quick_replies=None) -> requests.Response:
    url = "https://graph.facebook.com/v15.0/me/messages"
    headers = {
        "Authorization": f"Bearer {INSTAGRAM_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {"recipient": {"id": to}, "message": {"text": text}}

    # Note: Instagram Graph API doesn't natively support quick replies
    # like WhatsApp, but we can simulate it with templates or text.
    if quick_replies:
        # Append quick reply options as text
        options = "\n".join([f"- {btn['reply']['title']}" for btn in quick_replies])
        payload["message"]["text"] += f"\n\nOptions:\n{options}"

    return requests.post(url, json=payload, headers=headers)
