"""
ai_client.py — PRISM's shared AI reasoning layer.

Every "agent" in PRISM (Territory, Signal, Engagement, Activation, Dormant)
routes its generative/decision-making work through this module. The
Compliance agent (Layer 5) deliberately does NOT use this module —
compliance stays 100% deterministic rule-checking, on purpose, because
audit-critical decisions should never be probabilistic.

TWO SUPPORTED PROVIDERS — pick one via PRISM_AI_PROVIDER in .env:
  - "gemini"  -> Google Gemini (free tier, ~5 req/min limit on flash)
  - "nearai"  -> NEAR AI Cloud (pay-per-token, OpenAI-compatible endpoint,
                 hosts DeepSeek-V3.1/Qwen/etc — no per-minute free-tier
                 throttling like Gemini's free tier has)

If PRISM_AI_PROVIDER isn't set, auto-detects based on which API key is
present (NEAR_AI_API_KEY takes priority if both are set, since it has no
aggressive rate limit).

Design principle: AI-first, rules as a safety net.
- If a provider is configured -> every agent call below actually reasons
  with a real model and returns real, individually-generated content.
- If NOT configured -> each agent falls back to the original hardcoded
  rule/template logic, so the app still runs end-to-end without any key.
  Every response is tagged so the UI can show exactly which parts are
  live AI vs. fallback rules.

Gemini free key: https://aistudio.google.com/app/apikey
NEAR AI key (pay-per-token): https://cloud.near.ai/
"""

import os
import json
from typing import Optional, Dict, Any

try:
    import google.generativeai as genai
    _GEMINI_SDK_AVAILABLE = True
except ImportError:
    _GEMINI_SDK_AVAILABLE = False

try:
    from openai import OpenAI as _OpenAIClient
    _NEARAI_SDK_AVAILABLE = True
except ImportError:
    _NEARAI_SDK_AVAILABLE = False

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

NEAR_AI_API_KEY = os.getenv("NEAR_AI_API_KEY")
NEAR_AI_MODEL = os.getenv("NEAR_AI_MODEL", "deepseek-ai/DeepSeek-V3.1")
NEAR_AI_BASE_URL = "https://cloud-api.near.ai/v1"

# Which provider is active. "auto" prefers NEAR AI (no aggressive rate
# limit) if its key is present, else falls back to Gemini.
_PROVIDER_SETTING = os.getenv("PRISM_AI_PROVIDER", "auto").lower()

if _PROVIDER_SETTING == "nearai":
    PROVIDER = "nearai"
elif _PROVIDER_SETTING == "gemini":
    PROVIDER = "gemini"
else:  # auto
    PROVIDER = "nearai" if NEAR_AI_API_KEY else "gemini"

_gemini_model = None
_nearai_client = None
_call_count = 0
_fail_count = 0
_cache: Dict[str, Any] = {}


def is_ai_enabled() -> bool:
    """True only if the active provider's SDK is installed AND its key is configured."""
    if PROVIDER == "nearai":
        return _NEARAI_SDK_AVAILABLE and bool(NEAR_AI_API_KEY)
    return _GEMINI_SDK_AVAILABLE and bool(GEMINI_API_KEY)


def _get_gemini_model():
    global _gemini_model
    if _gemini_model is None and _GEMINI_SDK_AVAILABLE and GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(GEMINI_MODEL)
    return _gemini_model


def _get_nearai_client():
    global _nearai_client
    if _nearai_client is None and _NEARAI_SDK_AVAILABLE and NEAR_AI_API_KEY:
        _nearai_client = _OpenAIClient(base_url=NEAR_AI_BASE_URL, api_key=NEAR_AI_API_KEY)
    return _nearai_client


def get_ai_status() -> Dict[str, Any]:
    return {
        "ai_enabled": is_ai_enabled(),
        "provider": PROVIDER,
        "model": NEAR_AI_MODEL if PROVIDER == "nearai" else GEMINI_MODEL,
        "sdk_installed": _NEARAI_SDK_AVAILABLE if PROVIDER == "nearai" else _GEMINI_SDK_AVAILABLE,
        "api_key_configured": bool(NEAR_AI_API_KEY if PROVIDER == "nearai" else GEMINI_API_KEY),
        "calls_made": _call_count,
        "calls_failed": _fail_count,
        "mode": "live_agentic_ai" if is_ai_enabled() else "rule_based_fallback",
    }


def ask_ai(system_prompt: str, user_prompt: str, max_tokens: int = 1200,
           cache_key: Optional[str] = None, json_mode: bool = False) -> Optional[str]:
    """
    Core call: sends a system + user prompt to the active provider and
    returns plain text. Returns None (never raises) if AI is unavailable
    or the call fails — callers fall back to rule-based logic on None.

    Note: max_tokens defaults are generous because Devanagari/vernacular
    script (Hindi, Bhojpuri, etc.) consumes noticeably more tokens per
    character than English — too low a limit truncates output mid-string.
    """
    if cache_key and cache_key in _cache:
        return _cache[cache_key]
    if not is_ai_enabled():
        return None

    text = _ask_nearai(system_prompt, user_prompt, max_tokens, json_mode) if PROVIDER == "nearai" \
        else _ask_gemini(system_prompt, user_prompt, max_tokens, json_mode)

    if text is not None and cache_key:
        _cache[cache_key] = text
    return text


def _ask_gemini(system_prompt: str, user_prompt: str, max_tokens: int, json_mode: bool) -> Optional[str]:
    global _call_count, _fail_count
    try:
        model = _get_gemini_model()
        _call_count += 1
        full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
        gen_config_kwargs = {"max_output_tokens": max_tokens, "temperature": 0.7}
        if json_mode:
            gen_config_kwargs["response_mime_type"] = "application/json"
        response = model.generate_content(
            full_prompt, generation_config=genai.types.GenerationConfig(**gen_config_kwargs)
        )
        try:
            finish_reason = response.candidates[0].finish_reason
            if str(finish_reason) in ("2", "MAX_TOKENS", "FinishReason.MAX_TOKENS"):
                print(f"[PRISM ai_client] Gemini response truncated at max_tokens={max_tokens}, retrying higher")
                gen_config_kwargs["max_output_tokens"] = min(max_tokens * 2, 4096)
                response = model.generate_content(
                    full_prompt, generation_config=genai.types.GenerationConfig(**gen_config_kwargs)
                )
        except (IndexError, AttributeError):
            pass
        return (response.text or "").strip()
    except Exception as e:
        _fail_count += 1
        print(f"[PRISM ai_client] Gemini call failed, falling back to rules: {e}")
        return None


def _ask_nearai(system_prompt: str, user_prompt: str, max_tokens: int, json_mode: bool) -> Optional[str]:
    global _call_count, _fail_count
    try:
        client = _get_nearai_client()
        _call_count += 1
        kwargs = dict(
            model=NEAR_AI_MODEL,
            max_tokens=max_tokens,
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        if json_mode:
            # Not every model on NEAR AI's catalog supports response_format;
            # if this fails, we retry once without it below.
            kwargs["response_format"] = {"type": "json_object"}
        try:
            response = client.chat.completions.create(**kwargs)
        except Exception as inner_e:
            if json_mode:
                kwargs.pop("response_format", None)
                response = client.chat.completions.create(**kwargs)
            else:
                raise inner_e

        choice = response.choices[0]
        text = (choice.message.content or "").strip()

        # DeepSeek-class reasoning models can consume most of the token
        # budget on internal "thinking" before writing the visible answer,
        # so a small double (e.g. 600 -> 1200) often still isn't enough —
        # jump straight to a generous ceiling instead of incremental doubling.
        if choice.finish_reason == "length" or not text:
            reason = "truncated (finish_reason=length)" if choice.finish_reason == "length" else "empty content despite finish_reason=stop (likely consumed by internal reasoning tokens)"
            print(f"[PRISM ai_client] NEAR AI response {reason} at max_tokens={max_tokens}, retrying with higher budget")
            kwargs["max_tokens"] = 4096
            response = client.chat.completions.create(**kwargs)
            text = (response.choices[0].message.content or "").strip()
            if not text:
                print(f"[PRISM ai_client] NEAR AI still returned empty content after retry at max_tokens=4096 — "
                      f"finish_reason={response.choices[0].finish_reason}. This model may need thinking mode "
                      f"disabled; check NEAR_AI_MODEL in .env or try a non-reasoning model variant.")

        return text if text else None
    except Exception as e:
        _fail_count += 1
        print(f"[PRISM ai_client] NEAR AI call failed, falling back to rules: {e}")
        return None


def ask_ai_json(system_prompt: str, user_prompt: str, max_tokens: int = 1200,
                 cache_key: Optional[str] = None) -> Optional[dict]:
    """Same as ask_ai but parses the response as JSON. Returns None on any failure."""
    full_system = (
        system_prompt
        + "\n\nCRITICAL: Respond with ONLY valid JSON. No markdown code fences, "
          "no preamble, no explanation outside the JSON object. Keep prose fields "
          "concise (1-2 sentences) so the full response fits comfortably within the token limit."
    )
    raw = ask_ai(full_system, user_prompt, max_tokens=max_tokens, cache_key=cache_key, json_mode=True)
    if raw is None:
        return None
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except Exception as e:
        print(f"[PRISM ai_client] JSON parse failed: {e} — raw: {cleaned[:200]}")
        return None
