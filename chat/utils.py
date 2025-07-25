import os
import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

WHATSAPP_TOKEN   = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID  = os.getenv("PHONE_NUMBER_ID")
INSTAGRAM_TOKEN  = os.getenv("INSTAGRAM_TOKEN")

def send_whatsapp(to: str, text: str, quick_replies=None) -> requests.Response:
    url = f"https://graph.facebook.com/v15.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    if quick_replies:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {"buttons": quick_replies}
            }
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }

    # Debug output
    print(f"[DEBUG][WhatsApp] POST to {url}")
    print(f"[DEBUG][WhatsApp] Headers: {headers}")
    print(f"[DEBUG][WhatsApp] Payload: {payload}")

    resp = requests.post(url, json=payload, headers=headers)

    # Debug output
    print(f"[DEBUG][WhatsApp] Response status: {resp.status_code}")
    print(f"[DEBUG][WhatsApp] Response body: {resp.text}")

    # Also log
    logger.debug("→ WhatsApp payload: %s", payload)
    logger.debug("← WhatsApp API  %s %s", resp.status_code, resp.text)

    return resp

def send_instagram(to: str, text: str, quick_replies=None) -> requests.Response:
    url = "https://graph.facebook.com/v15.0/me/messages"
    headers = {
        "Authorization": f"Bearer {INSTAGRAM_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {"recipient": {"id": to}, "message": {"text": text}}

    if quick_replies:
        options = "\n".join(f"- {b['reply']['title']}" for b in quick_replies)
        payload["message"]["text"] += f"\n\nOptions:\n{options}"

    # Debug output
    print(f"[DEBUG][Instagram] POST to {url}")
    print(f"[DEBUG][Instagram] Headers: {headers}")
    print(f"[DEBUG][Instagram] Payload: {payload}")

    resp = requests.post(url, json=payload, headers=headers)

    # Debug output
    print(f"[DEBUG][Instagram] Response status: {resp.status_code}")
    print(f"[DEBUG][Instagram] Response body: {resp.text}")

    # Also log
    logger.debug("→ Instagram payload: %s", payload)
    logger.debug("← Instagram API %s %s", resp.status_code, resp.text)

    return resp
