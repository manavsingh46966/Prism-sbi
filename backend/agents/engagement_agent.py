import random
import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ai_client import ask_ai_json, is_ai_enabled, get_ai_status
from sarvam_client import text_to_speech, is_sarvam_enabled, get_sarvam_status
from whatsapp_client import send_template_message, send_freeform_message, is_whatsapp_enabled, get_whatsapp_status

# ── Fallback templates (used only when no GEMINI_API_KEY is configured) ──
# These are the ORIGINAL static scripts. Kept intentionally so the app still
# runs end-to-end without a key, but they are no longer the primary path.

_FALLBACK_VOICE_SCRIPTS = {
    "farmer": {
        "Hindi": "Namaste! Main SBI ki taraf se bol raha hoon. Aapke liye Kisan Savings Account bilkul free mein khul sakta hai. Koi minimum balance nahi. DBT seedha khate mein aayega.",
        "Bhojpuri": "Pranam! Hum SBI se baat kar rahe bani. Aapan khatiir Kisan Savings Account bilkul muft mein khul sake la. DBT seedha khataa mein aai.",
    },
    "gig_worker": {
        "Hindi": "Hello! Aapki delivery income ko SBI mein safe rakhen. Zero balance account, UPI enabled, instant transfer.",
    },
    "kirana": {
        "Hindi": "Namaskar! Aapke business ke liye SBI Current Account — overdraft facility bhi milegi.",
    },
    "first_timer": {
        "Hindi": "Hello! Pehla bank account kholna ab bahut aasaan hai. SBI mein online ya BC agent se ghar baithe kholen.",
    },
}

_FALLBACK_WHATSAPP = {
    "farmer": "🌾 *SBI Kisan Account* खोलें — बिल्कुल मुफ्त!\n✅ Zero balance\n✅ DBT direct credit\n\nअभी शुरू करें: *KISAN* लिखकर भेजें",
    "gig_worker": "🛵 *SBI Savings Account* — आपकी income के लिए\n✅ Zero balance\n✅ UPI enabled\n\nशुरू करें: *OPEN* लिखकर भेजें",
    "kirana": "🏪 *SBI Business Account* — आपके business के लिए\n✅ Overdraft facility\n\nजानें: *BUSINESS* लिखकर भेजें",
    "first_timer": "👋 *SBI Savings Account* — पहला कदम!\n✅ Online KYC\n✅ Instant account\n\nशुरू करें: *START* लिखकर भेजें",
    "nri": "🌍 *SBI NRE Account* — Send money home!\n✅ Tax-free returns\n\nApply: Reply *NRE*",
}


class EngagementAgent:
    def __init__(self):
        self.engagements = []
        self.engagement_counter = 0
        self.sarvam_api_key = os.getenv("SARVAM_API_KEY", "demo_mode")
        self.whatsapp_token = os.getenv("WHATSAPP_TOKEN", "demo_mode")

    def trigger_engagement(self, individual: Dict, compliance_cleared: bool = True) -> Dict:
        if not compliance_cleared:
            return {"success": False, "reason": "Compliance check failed"}

        channel = individual.get("preferred_channel", "voice")
        persona = individual.get("persona_type", "first_timer")
        language = individual.get("language", "Hindi")

        self.engagement_counter += 1
        engagement_id = f"ENG{self.engagement_counter:04d}"

        if channel == "voice":
            result = self._trigger_voice_call(individual, language, persona)
        elif channel == "whatsapp":
            result = self._trigger_whatsapp(individual, language, persona)
        elif channel == "ussd":
            result = self._trigger_ussd(individual, language, persona)
        else:
            result = self._trigger_inapp(individual, language, persona)

        engagement = {
            "id": engagement_id,
            "individual_id": individual.get("id"),
            "individual_name": individual.get("name"),
            "channel": channel,
            "language": language,
            "persona": persona,
            "message": result.get("message", ""),
            "status": result.get("status", "sent"),
            "triggered_at": datetime.utcnow().isoformat(),
            "estimated_response_time": result.get("response_time", "2-4 hours"),
            "compliance_cleared": compliance_cleared,
            "agent_id": "PRISM-ENG-01",
            "ai_generated": result.get("ai_generated", False),
            "agent_mode": result.get("agent_mode", "rule_based_fallback"),
            "agent_reasoning": result.get("agent_reasoning"),
            "demo_note": result.get("demo_note"),
            # Real delivery fields — pass through whatever the channel handler
            # produced (audio for voice, WhatsApp confirmation, etc). Using
            # **result last would risk clobbering the curated keys above, so
            # we explicitly whitelist the extra delivery-specific keys instead.
            "audio_base64": result.get("audio_base64"),
            "audio_format": result.get("audio_format"),
            "voice_model": result.get("voice_model"),
            "voice_delivery_real": result.get("voice_delivery_real"),
            "whatsapp_delivery_real": result.get("whatsapp_delivery_real"),
            "delivery_mode": result.get("delivery_mode"),
            "whatsapp_message_id": result.get("whatsapp_message_id"),
            "delivery_real": result.get("delivery_real"),
            "platform": result.get("platform"),
            "ussd_code": result.get("ussd_code"),
            "gateway": result.get("gateway"),
        }
        self.engagements.append(engagement)
        return engagement

    # ── Shared AI content generator ──────────────────────────────────────────

    def _ai_generate_outreach(self, ind: Dict, language: str, persona: str, channel: str) -> Dict:
        """
        Agentic step: instead of picking a pre-written script from a dict,
        Gemini writes the actual outreach content for THIS specific person —
        using their name, persona, signals, language and the channel's real
        constraints (voice = spoken/short, WhatsApp = can use formatting/
        emoji, USSD = must be a plain-text menu under strict char limits).
        It also explains its channel/timing/tone reasoning, which is the
        "agentic" trace shown in the demo.
        """
        if not is_ai_enabled():
            return {}

        channel_constraints = {
            "voice": "This will be spoken aloud by a vernacular voice AI (Sarvam AI). "
                     "Write natural spoken language, 2-4 sentences, no emojis, no formatting, "
                     "in the specified language/dialect. It must sound like a real person talking, "
                     "not a written notice.",
            "whatsapp": "This is a WhatsApp Business message. You may use 1-2 relevant emojis, "
                        "short bold-style emphasis with *asterisks*, bullet points with checkmarks, and a clear "
                        "one-word reply call-to-action at the end (e.g. reply KISAN).",
            "ussd": "This is a USSD menu shown on a basic feature phone screen with NO internet and a "
                    "strict ~140 character limit. Plain text only, numbered menu options, no emojis.",
            "in_app": "This is a push notification inside the YONO SBI app. One short, friendly sentence, "
                      "under 25 words.",
        }

        system_prompt = (
            "You are PRISM's Hyper-contextual Engagement Agent for SBI's customer acquisition system. "
            "Your job is to write ONE real outreach message for ONE specific real individual, personalized "
            "to their persona, language, and financial signals — never a generic bank ad. "
            + channel_constraints.get(channel, "")
        )

        user_prompt = f"""Write outreach content for:
Name: {ind.get('name')}
Persona: {persona}
Language required: {language}
Channel: {channel}
Age: {ind.get('age')}
Income estimate: Rs {ind.get('income_estimate')}/month
DBT recipient: {ind.get('dbt_recipient')}
UPI active (no savings account): {ind.get('upi_active')}
Has smartphone: {ind.get('has_smartphone')}
Financial readiness score: {ind.get('financial_readiness_score')}

Return JSON:
{{
  "message": "<the actual outreach content, following the channel constraints above, in {language} where the persona calls for a vernacular tone>",
  "reasoning": "<one sentence: why this tone/offer/timing fits this specific person>",
  "recommended_timing": "<best time of day to send this, and why, tied to this persona's daily routine>"
}}"""

        result = ask_ai_json(
            system_prompt, user_prompt, max_tokens=900,
            cache_key=f"engage_{channel}_{ind.get('id')}"
        )
        return result or {}

    # ── Channel handlers ─────────────────────────────────────────────────────

    def _trigger_voice_call(self, ind: Dict, language: str, persona: str) -> Dict:
        ai_result = self._ai_generate_outreach(ind, language, persona, "voice")

        script_text = ai_result.get("message") if ai_result.get("message") else (
            _FALLBACK_VOICE_SCRIPTS.get(persona, {}).get(language)
            or _FALLBACK_VOICE_SCRIPTS.get(persona, {}).get("Hindi", "SBI mein khata kholen")
        )
        content_is_ai = bool(ai_result.get("message"))

        # Real delivery step: actually generate spoken audio via Sarvam AI.
        # This is genuine — if it succeeds, audio_base64 is real synthesized
        # speech the frontend can play, not a label.
        audio_result = text_to_speech(script_text, language=language)

        base = {
            "status": "call_initiated",
            "message": script_text,
            "call_duration": "90 seconds",
            "voice_model": audio_result["voice_model"] if audio_result else "Sarvam AI — Bulbul v3 (not connected)",
            "language_model": f"Sarvam {language}",
            "response_time": ai_result.get("recommended_timing", "Immediate") if content_is_ai else "Immediate",
            "ai_generated": content_is_ai,
            "agent_mode": "live_agentic_ai" if content_is_ai else "rule_based_fallback",
            "agent_reasoning": ai_result.get("reasoning") if content_is_ai else None,
        }

        if audio_result:
            base["audio_base64"] = audio_result["audio_base64"]
            base["audio_format"] = audio_result["audio_format"]
            base["voice_delivery_real"] = True
            base["demo_note"] = (
                "Real: script written live by Gemini, then genuinely synthesized to speech by Sarvam AI. "
                "Play the audio below — this is actual generated audio, not a label."
                if content_is_ai else
                "Fallback script template, but genuinely synthesized to real audio by Sarvam AI."
            )
        else:
            base["voice_delivery_real"] = False
            base["demo_note"] = (
                ("Voice script generated live by Gemini. " if content_is_ai else "Rule-based fallback script. ")
                + "No real audio generated — set SARVAM_API_KEY in backend/.env to enable real TTS."
            )

        return base

    def _trigger_whatsapp(self, ind: Dict, language: str, persona: str) -> Dict:
        ai_result = self._ai_generate_outreach(ind, language, persona, "whatsapp")

        content_is_ai = bool(ai_result.get("message"))
        msg = ai_result.get("message") if content_is_ai else _FALLBACK_WHATSAPP.get(
            persona, "SBI account kholne ke liye reply karein"
        )

        # Real delivery attempt via Meta's WhatsApp Cloud API. Freeform text
        # only works if the recipient messaged your test number in the last
        # 24h (Meta platform rule) — otherwise we send the real, pre-approved
        # "hello_world" template so the pipe is still genuinely proven live.
        delivery_result = None
        if is_whatsapp_enabled():
            phone = ind.get("phone")
            delivery_result = send_freeform_message(phone, msg) if phone else None
            if not delivery_result:
                delivery_result = send_template_message()

        base = {
            "status": "message_sent",
            "message": msg,
            "platform": "WhatsApp Business API" + (" (Meta Cloud API)" if is_whatsapp_enabled() else " (not connected)"),
            "phone": ind.get("phone"),
            "response_time": ai_result.get("recommended_timing", "2-4 hours") if content_is_ai else "2-4 hours",
            "ai_generated": content_is_ai,
            "agent_mode": "live_agentic_ai" if content_is_ai else "rule_based_fallback",
            "agent_reasoning": ai_result.get("reasoning") if content_is_ai else None,
        }

        if delivery_result and delivery_result.get("delivered"):
            base["whatsapp_delivery_real"] = True
            base["delivery_mode"] = delivery_result["delivery_mode"]
            base["whatsapp_message_id"] = delivery_result.get("whatsapp_message_id")
            if delivery_result["delivery_mode"] == "real_template_message":
                base["demo_note"] = (
                    "Real delivery: Meta's pre-approved 'hello_world' template was actually sent to "
                    f"{delivery_result.get('to')} via WhatsApp — check that phone. Freeform personalized "
                    "text (shown above) requires the recipient to message the test number first, or an "
                    "approved custom template — that's a Meta platform rule, not a PRISM limitation."
                )
            else:
                base["demo_note"] = "Real delivery: the AI-generated message above was actually sent via WhatsApp."
        else:
            base["whatsapp_delivery_real"] = False
            base["demo_note"] = (
                ("Message generated live by Gemini. " if content_is_ai else "Rule-based fallback template. ")
                + "No real WhatsApp message sent — set WHATSAPP_TOKEN + WHATSAPP_PHONE_NUMBER_ID in "
                  "backend/.env to enable real delivery."
            )

        return base

    def _trigger_ussd(self, ind: Dict, language: str, persona: str) -> Dict:
        """
        NOTE ON REALISM: unlike voice (Sarvam) and WhatsApp (Meta Cloud API),
        USSD delivery cannot be made genuinely real by any individual or
        hackathon team — it requires a commercial aggregator agreement with
        a telecom operator (Airtel/BSNL/Jio), which only an actual bank/
        enterprise can obtain. This stays a clearly-labeled simulation: the
        menu TEXT is real (AI-generated), the delivery is not.
        """
        ai_result = self._ai_generate_outreach(ind, language, persona, "ussd")

        if ai_result.get("message"):
            return {
                "status": "ussd_simulated",
                "message": ai_result["message"],
                "ussd_code": "*222*1#",
                "gateway": "BSNL/Airtel USSD Gateway (SIMULATED — requires telecom aggregator contract, not achievable in a prototype)",
                "works_on": "Any phone — no internet needed",
                "response_time": "Immediate",
                "demo_note": "SIMULATED delivery. Menu text generated live by Gemini, within real feature-phone character limits — but no actual USSD session is opened. Real USSD requires a paid telecom aggregator agreement no hackathon team can obtain.",
                "ai_generated": True,
                "agent_mode": "live_agentic_ai",
                "agent_reasoning": ai_result.get("reasoning"),
                "delivery_real": False,
            }

        ussd_flow = "*222*1# — SBI PRISM\n1. Naya Khata Kholen\n2. Loan Jaankari\n3. BC Agent Bulayein\n4. Madad"
        return {
            "status": "ussd_simulated",
            "message": ussd_flow,
            "ussd_code": "*222*1#",
            "gateway": "BSNL/Airtel USSD Gateway (SIMULATED)",
            "works_on": "Any phone — no internet needed",
            "response_time": "Immediate",
            "demo_note": "SIMULATED delivery, rule-based fallback menu. Real USSD requires a telecom aggregator agreement.",
            "ai_generated": False,
            "agent_mode": "rule_based_fallback",
            "agent_reasoning": None,
            "delivery_real": False,
        }

    def _trigger_inapp(self, ind: Dict, language: str, persona: str) -> Dict:
        ai_result = self._ai_generate_outreach(ind, language, persona, "in_app")
        if ai_result.get("message"):
            return {
                "status": "notification_simulated",
                "message": ai_result["message"],
                "platform": "YONO SBI / Partner App (SIMULATED — no real app integration)",
                "response_time": ai_result.get("recommended_timing", "Real-time"),
                "demo_note": "SIMULATED delivery. Notification copy generated live by Gemini, but not actually pushed to any app — that requires SBI's own app infrastructure.",
                "ai_generated": True,
                "agent_mode": "live_agentic_ai",
                "agent_reasoning": ai_result.get("reasoning"),
                "delivery_real": False,
            }
        return {
            "status": "notification_simulated",
            "message": "Personalized in-app notification delivered via push",
            "platform": "YONO SBI / Partner App (SIMULATED)",
            "response_time": "Real-time",
            "demo_note": "SIMULATED delivery, rule-based fallback copy.",
            "ai_generated": False,
            "agent_mode": "rule_based_fallback",
            "agent_reasoning": None,
            "delivery_real": False,
        }

    def get_engagement_history(self, individual_id: int = None) -> List[Dict]:
        if individual_id:
            return [e for e in self.engagements if e.get("individual_id") == individual_id]
        return self.engagements

    def get_bc_dispatch(self, individual: Dict) -> Dict:
        """
        SIMULATED. Dispatching a real human BC (Business Correspondent)
        agent requires an actual employed workforce — there is no API for
        this and no prototype can make it real. Kept as a clearly-labeled
        mock so the concept can still be demoed honestly.
        """
        return {
            "dispatch_id": f"BC{random.randint(10000, 99999)}",
            "bc_agent": f"BC Agent #{random.randint(100, 999)}",
            "bc_name": "Rajesh Kumar",
            "area": individual.get("area", "Varanasi"),
            "individual_name": individual.get("name"),
            "phone": individual.get("phone"),
            "pre_filled_form": {
                "name": individual.get("name"),
                "age": individual.get("age"),
                "pincode": individual.get("pincode"),
                "language": individual.get("language"),
                "recommended_product": "Kisan Savings Account",
                "documents_needed": ["Aadhaar Card", "PAN (optional)", "Photo"],
            },
            "script": f"Visit {individual.get('name')} for Kisan Savings Account. Pre-qualified. Readiness score: {individual.get('financial_readiness_score')}",
            "estimated_visit": "Within 24 hours",
            "status": "dispatched_simulated",
            "delivery_real": False,
            "demo_note": "SIMULATED — dispatching a real BC agent requires an actual employed workforce, not something any software integration can provide.",
        }

    def get_stats(self) -> Dict:
        total = len(self.engagements)
        by_channel = {}
        ai_generated_count = 0
        for e in self.engagements:
            ch = e["channel"]
            by_channel[ch] = by_channel.get(ch, 0) + 1
            if e.get("ai_generated"):
                ai_generated_count += 1
        return {
            "total_engagements": total,
            "by_channel": by_channel,
            "estimated_conversions": int(total * 0.32),
            "avg_response_rate": "34%",
            "ai_generated_engagements": ai_generated_count,
            "ai_status": get_ai_status(),
            "sarvam_status": get_sarvam_status(),
            "whatsapp_status": get_whatsapp_status(),
        }
