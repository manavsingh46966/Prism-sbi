"""
sarvam_client.py — Real integration with Sarvam AI's Text-to-Speech API
(Bulbul v3), which genuinely converts PRISM's AI-generated voice scripts
into actual spoken audio in Indian languages.

Docs: https://docs.sarvam.ai/api-reference-docs/endpoints/text-to-speech
Free API key (no credit card): https://dashboard.sarvam.ai/

Unlike ai_client.py's LLM calls, this returns real audio bytes (base64 WAV/MP3)
that the frontend can actually play — this is a genuine "delivery" integration,
not just content generation.
"""

import os
import base64
from typing import Optional, Dict

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_BASE_URL = "https://api.sarvam.ai/text-to-speech"

# PRISM's persona languages -> nearest Sarvam-supported BCP-47 code.
# Sarvam doesn't have a distinct Bhojpuri code, so it falls back to Hindi
# (closest supported language, mutually intelligible for TTS purposes).
_LANGUAGE_MAP = {
    "Hindi": "hi-IN",
    "Bhojpuri": "hi-IN",
    "Bengali": "bn-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN",
    "Odia": "od-IN",
    "Punjabi": "pa-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Gujarati": "gu-IN",
    "English": "en-IN",
}

_call_count = 0
_fail_count = 0


def is_sarvam_enabled() -> bool:
    return _REQUESTS_AVAILABLE and bool(SARVAM_API_KEY)


def get_sarvam_status() -> Dict:
    return {
        "sarvam_enabled": is_sarvam_enabled(),
        "calls_made": _call_count,
        "calls_failed": _fail_count,
    }


def text_to_speech(text: str, language: str = "Hindi", speaker: str = "priya",
                    pace: float = 1.0) -> Optional[Dict]:
    """
    Calls Sarvam AI's real TTS API and returns actual generated audio.

    Returns None if Sarvam isn't configured or the call fails — callers
    should treat this as "voice content exists (from Gemini) but no real
    audio was generated", same fallback philosophy as ai_client.py.

    On success, returns:
        {"audio_base64": "...", "audio_format": "wav", "voice_model": "bulbul:v3", "speaker": "priya"}
    """
    global _call_count, _fail_count

    if not is_sarvam_enabled():
        return None
    if not text or not text.strip():
        return None

    lang_code = _LANGUAGE_MAP.get(language, "hi-IN")

    # Sarvam's REST TTS endpoint caps at ~2500 characters per request.
    trimmed_text = text.strip()[:2000]

    try:
        _call_count += 1
        response = requests.post(
            SARVAM_BASE_URL,
            headers={
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": trimmed_text,
                "target_language_code": lang_code,
                "speaker": speaker,
                "pace": pace,
                "model": "bulbul:v3",
                "output_audio_codec": "wav",
            },
            timeout=20,
        )
        if response.status_code != 200:
            print(f"[PRISM sarvam_client] TTS API error {response.status_code}: {response.text[:300]}")
            _fail_count += 1
            return None

        result = response.json()
        audios = result.get("audios", [])
        if not audios:
            _fail_count += 1
            return None

        return {
            "audio_base64": audios[0],
            "audio_format": "wav",
            "voice_model": "bulbul:v3",
            "speaker": speaker,
            "language_code": lang_code,
        }
    except Exception as e:
        _fail_count += 1
        print(f"[PRISM sarvam_client] TTS call failed: {e}")
        return None
