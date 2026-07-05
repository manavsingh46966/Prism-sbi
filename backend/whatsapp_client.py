"""
whatsapp_client.py — Real integration with Meta's WhatsApp Cloud API.

Setup (free, no business verification needed for TESTING):
1. Create a Meta Developer app at https://developers.facebook.com/apps
2. Add the "WhatsApp" product — Meta gives you a free TEST phone number
3. In the WhatsApp > API Setup screen, add up to 5 recipient numbers to the
   "To" test list (your own phone works) — Meta only lets you message
   numbers you've explicitly added in test mode.
4. Copy the temporary access token + Phone Number ID into .env

IMPORTANT PLATFORM LIMITATION (this is a Meta rule, not a PRISM bug):
WhatsApp does NOT allow sending arbitrary freeform text to someone who
hasn't messaged your business number in the last 24 hours. Outside that
window, you can ONLY send a pre-approved message template. Every test
number comes with exactly one pre-approved template: "hello_world".

So real behavior here is:
- If the recipient messaged your test number in the last 24h -> PRISM can
  send the actual AI-generated personalized text for real.
- Otherwise -> PRISM sends the "hello_world" template for real (this DOES
  arrive on the recipient's phone, genuinely, proving the pipe works end
  to end) and returns the AI-generated text separately so the demo can
  still show what a real customer message would have said.

This is disclosed in the API response via "delivery_mode" so nothing is
silently overstated.
"""

import os
from typing import Optional, Dict

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
# Must be a number YOU added to your Meta test app's allowed recipient list.
WHATSAPP_TEST_RECIPIENT = os.getenv("WHATSAPP_TEST_RECIPIENT")

GRAPH_API_VERSION = "v21.0"

_call_count = 0
_fail_count = 0


def is_whatsapp_enabled() -> bool:
    return _REQUESTS_AVAILABLE and bool(WHATSAPP_TOKEN) and bool(WHATSAPP_PHONE_NUMBER_ID)


def get_whatsapp_status() -> Dict:
    return {
        "whatsapp_enabled": is_whatsapp_enabled(),
        "test_recipient_configured": bool(WHATSAPP_TEST_RECIPIENT),
        "calls_made": _call_count,
        "calls_failed": _fail_count,
    }


def send_template_message(to_number: Optional[str] = None) -> Optional[Dict]:
    """
    Sends Meta's pre-approved "hello_world" template — this is the ONE
    message any freshly-created WhatsApp test app can send to a new
    recipient without a 24h session or custom template approval. Sending
    this successfully is real proof the integration works end-to-end.
    """
    global _call_count, _fail_count

    if not is_whatsapp_enabled():
        return None

    recipient = to_number or WHATSAPP_TEST_RECIPIENT
    if not recipient:
        print("[PRISM whatsapp_client] No recipient number configured (WHATSAPP_TEST_RECIPIENT)")
        return None

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    try:
        _call_count += 1
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
            json={
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "template",
                "template": {"name": "hello_world", "language": {"code": "en_US"}},
            },
            timeout=15,
        )
        if response.status_code != 200:
            print(f"[PRISM whatsapp_client] Send failed {response.status_code}: {response.text[:300]}")
            _fail_count += 1
            return None
        result = response.json()
        return {
            "delivered": True,
            "delivery_mode": "real_template_message",
            "whatsapp_message_id": result.get("messages", [{}])[0].get("id"),
            "to": recipient,
            "note": "Meta's pre-approved 'hello_world' template was sent for real — WhatsApp "
                    "doesn't allow custom freeform text outside a 24h user-initiated session "
                    "or without an approved template, so this proves real delivery without "
                    "requiring template approval first.",
        }
    except Exception as e:
        _fail_count += 1
        print(f"[PRISM whatsapp_client] Send failed: {e}")
        return None


def send_freeform_message(to_number: str, text: str) -> Optional[Dict]:
    """
    Sends real freeform text — only works if `to_number` messaged your
    WhatsApp test number within the last 24 hours (Meta's session-window
    rule). Will fail with a clear Meta error otherwise; that failure is
    expected platform behavior, not a bug.
    """
    global _call_count, _fail_count

    if not is_whatsapp_enabled():
        return None

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    try:
        _call_count += 1
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
            json={
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {"body": text[:4096]},
            },
            timeout=15,
        )
        if response.status_code != 200:
            print(f"[PRISM whatsapp_client] Freeform send failed (likely outside 24h session window): "
                  f"{response.status_code}: {response.text[:300]}")
            _fail_count += 1
            return None
        result = response.json()
        return {
            "delivered": True,
            "delivery_mode": "real_freeform_message",
            "whatsapp_message_id": result.get("messages", [{}])[0].get("id"),
            "to": to_number,
        }
    except Exception as e:
        _fail_count += 1
        print(f"[PRISM whatsapp_client] Freeform send failed: {e}")
        return None
