import os
import logging
import openai

# Set your OpenAI key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

# Enable debug logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Sushi menu sample (could be moved to DB)
MENU = """
🍣 *Sushi Run Menu*:
- Salmon Roll – ₡3500
- Tuna Roll – ₡3700
- California Roll – ₡3300
- Spicy Mayo Add-on – ₡500
- Ginger + Wasabi Pack – ₡300
Delivery: ₡1000 in San Marcos / ₡1500 nearby towns
"""

HOURS = "We're open from 12 PM to 8 PM, Tuesday to Sunday! 🕗"
LOCATION = "📍 We deliver from San Marcos de Tarrazú. Local pickup available too!"

# Basic keyword-based rules
def keyword_reply(text):
    text = text.lower()
    logger.debug(f"Checking keywords in text: {text}")

    if "menu" in text:
        return MENU
    elif "hours" in text or "open" in text:
        return HOURS
    elif "location" in text or "where" in text or "pickup" in text:
        return LOCATION
    elif "hi" in text or "hello" in text or "hola" in text:
        return "Hey there! 👋 Welcome to Sushi Run 🍣 How can I help you today?"
    return None  # fallback to OpenAI

# OpenAI fallback for more natural replies
def openai_reply(text):
    logger.debug(f"Sending message to OpenAI: {text}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "You are a friendly chatbot assistant for a small home-based sushi delivery business "
                    "called Sushi Run. Always be polite, brief, and helpful. Mention the menu if asked, hours if relevant, "
                    "and offer delivery or pickup from San Marcos."
                )},
                {"role": "user", "content": text}
            ],
            temperature=0.7
        )
        reply_text = response["choices"][0]["message"]["content"]
        logger.debug(f"OpenAI response: {reply_text}")
        return reply_text
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "Sorry! I'm having trouble answering that right now. Can you ask again later?"

# Full reply logic
def generate_reply(text):
    logger.info(f"Incoming message: {text}")
    
    reply = keyword_reply(text)
    if reply:
        logger.info("Matched keyword rule.")
        return reply

    logger.info("Falling back to OpenAI.")
    return openai_reply(text)

# Optional: add quick replies/buttons
def get_quick_replies():
    return [
        {"type": "reply", "reply": {"id": "menu", "title": "🍣 View Menu"}},
        {"type": "reply", "reply": {"id": "hours", "title": "⏰ Hours"}},
        {"type": "reply", "reply": {"id": "location", "title": "📍 Location"}},
    ]
