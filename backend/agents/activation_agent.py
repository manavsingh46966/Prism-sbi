import random
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ai_client import ask_ai_json, is_ai_enabled

class ActivationAgent:
    def __init__(self):
        self.activations = {}

    def create_activation(self, individual: Dict) -> Dict:
        ind_id = individual.get("id")
        persona = individual.get("persona_type", "first_timer")
        language = individual.get("language", "Hindi")
        score = individual.get("financial_readiness_score", 50)

        timeline = self._generate_timeline(individual)
        journey = self._generate_90day_journey(individual)

        activation = {
            "individual_id": ind_id,
            "individual_name": individual.get("name"),
            "persona": persona,
            "language": language,
            "readiness_score": score,
            "account_opened_at": datetime.utcnow().isoformat(),
            "timeline": timeline,
            "journey": journey,
            "current_day": random.randint(1, 85),
            "status": "active" if score > 60 else "at_risk",
            "products_adopted": self._initial_products(persona),
            "activation_score": round(score * 0.85 + random.uniform(0, 10), 1),
            "next_nudge": self._next_nudge(individual, timeline),
            "churn_risk": "Low" if score > 70 else "Medium" if score > 45 else "High",
        }
        self.activations[ind_id] = activation
        return activation

    def _generate_timeline(self, ind: Dict) -> List[Dict]:
        score = ind.get("financial_readiness_score", 50)
        persona = ind.get("persona_type", "first_timer")
        language = ind.get("language", "Hindi")
        base = datetime.now() - timedelta(days=random.randint(5, 80))

        days_to_first = (
            random.randint(1, 4) if score > 70 else
            random.randint(3, 10) if score > 50 else
            random.randint(7, 20)
        )

        events = [
            {"day": 0, "event": "Account successfully opened", "type": "milestone", "date": base.strftime("%d %b %Y"), "icon": "✅"},
            {"day": 1, "event": f"Welcome message sent in {language}", "type": "nudge", "date": (base + timedelta(1)).strftime("%d %b %Y"), "icon": "👋"},
        ]

        if days_to_first > 3:
            events.append({"day": 3, "event": f"No transaction — personalised nudge sent in {language}", "type": "nudge", "date": (base + timedelta(3)).strftime("%d %b %Y"), "icon": "🔔"})

        events.append({"day": days_to_first, "event": f"First UPI transaction — ₹{random.randint(50, 800)}", "type": "milestone", "date": (base + timedelta(days_to_first)).strftime("%d %b %Y"), "icon": "💳"})

        if persona == "farmer":
            events.append({"day": 10, "event": "Kisan Credit Card eligibility check triggered", "type": "suggestion", "date": (base + timedelta(10)).strftime("%d %b %Y"), "icon": "🌾"})
            events.append({"day": 20, "event": "Fasal Bima Yojana enrollment suggested", "type": "suggestion", "date": (base + timedelta(20)).strftime("%d %b %Y"), "icon": "🛡️"})
        elif persona == "gig_worker":
            events.append({"day": 7, "event": "UPI merchant QR code issued", "type": "milestone", "date": (base + timedelta(7)).strftime("%d %b %Y"), "icon": "📱"})
            events.append({"day": 14, "event": "Recurring deposit suggestion — ₹500/month", "type": "suggestion", "date": (base + timedelta(14)).strftime("%d %b %Y"), "icon": "💰"})
        elif persona == "kirana":
            events.append({"day": 5, "event": "Business current account upgrade suggested", "type": "suggestion", "date": (base + timedelta(5)).strftime("%d %b %Y"), "icon": "🏪"})
            events.append({"day": 15, "event": "SME loan pre-approval notification sent", "type": "suggestion", "date": (base + timedelta(15)).strftime("%d %b %Y"), "icon": "📋"})
        elif persona == "first_timer":
            events.append({"day": 7, "event": "Financial literacy module completed", "type": "milestone", "date": (base + timedelta(7)).strftime("%d %b %Y"), "icon": "📚"})
            events.append({"day": 15, "event": "Fixed deposit suggestion — ₹5,000 idle balance", "type": "suggestion", "date": (base + timedelta(15)).strftime("%d %b %Y"), "icon": "🏦"})

        events.append({"day": 30, "event": "30-day review — engagement journey complete", "type": "milestone", "date": (base + timedelta(30)).strftime("%d %b %Y"), "icon": "🎯"})
        events.append({"day": 60, "event": "Second product adopted", "type": "milestone", "date": (base + timedelta(60)).strftime("%d %b %Y"), "icon": "⭐"})
        events.append({"day": 90, "event": "Fully activated customer — PRISM mission complete", "type": "success", "date": (base + timedelta(90)).strftime("%d %b %Y"), "icon": "🏆"})

        return sorted(events, key=lambda x: x["day"])

    def _generate_90day_journey(self, ind: Dict) -> List[Dict]:
        persona = ind.get("persona_type", "first_timer")
        language = ind.get("language", "Hindi")
        journey = []
        for week in range(1, 14):
            day = week * 7
            if week <= 2:
                action = f"Daily engagement nudge in {language} — build habit"
            elif week <= 4:
                action = "Weekly product recommendation based on transaction patterns"
            elif week <= 8:
                action = "Bi-weekly financial health check"
            else:
                action = "Monthly loyalty reward and cross-sell offer"
            journey.append({"week": week, "day": day, "action": action, "automated": True})
        return journey

    def _initial_products(self, persona: str) -> List[str]:
        products = {"farmer": ["Savings Account"], "gig_worker": ["Savings Account", "UPI"], "kirana": ["Current Account"], "first_timer": ["Savings Account"], "nri": ["NRE Account"]}
        return products.get(persona, ["Savings Account"])

    def _next_nudge(self, individual: Dict, timeline: List[Dict]) -> Dict:
        """
        Agentic step: rather than looking up a fixed message per persona,
        Claude decides the next best nudge by reasoning over this specific
        customer's actual activation timeline so far (what's already
        happened, what day they're on, their readiness score) — the same
        way a real growth/retention analyst would decide the next touch.
        Falls back to the original static nudge map if AI is unavailable.
        """
        persona = individual.get("persona_type", "first_timer")
        language = individual.get("language", "Hindi")

        ai_nudge = self._ai_next_nudge(individual, timeline)
        if ai_nudge:
            ai_nudge["ai_generated"] = True
            ai_nudge["agent_mode"] = "live_agentic_ai"
            return ai_nudge

        fallback_nudges = {
            "farmer": {"message": "Aapke khate mein ₹2,000 idle hain — Kisan RD shuru karein", "channel": "voice", "timing": "Tomorrow 8 AM"},
            "gig_worker": {"message": "Aaj ki delivery income save karein — Auto-sweep FD", "channel": "whatsapp", "timing": "Tonight 9 PM"},
            "kirana": {"message": "Aapka business 3 months active — SME loan eligible hain", "channel": "whatsapp", "timing": "Tomorrow 2 PM"},
            "first_timer": {"message": "Pehla mahina complete — FD ka option dekhein", "channel": "in_app", "timing": "Today 6 PM"},
            "nri": {"message": "Remittance rate today: ₹83.5/USD — transfer now?", "channel": "whatsapp", "timing": "Now"},
        }
        result = dict(fallback_nudges.get(persona, {"message": "SBI app use karein", "channel": "whatsapp", "timing": "Today"}))
        result["ai_generated"] = False
        result["agent_mode"] = "rule_based_fallback"
        return result

    def _ai_next_nudge(self, individual: Dict, timeline: List[Dict]) -> Dict:
        if not is_ai_enabled():
            return None

        persona = individual.get("persona_type", "first_timer")
        language = individual.get("language", "Hindi")
        score = individual.get("financial_readiness_score", 50)
        recent_events = [f"Day {e['day']}: {e['event']}" for e in timeline[-4:]]

        system_prompt = (
            "You are PRISM's Activation Intelligence Agent for SBI. Your job is to decide the SINGLE "
            "next best action for a newly-onboarded customer, based on their actual activation timeline "
            "so far — like a retention analyst deciding the next best touch, not a scheduled template."
        )
        user_prompt = f"""Customer: {individual.get('name')}, persona: {persona}, language: {language}, readiness score: {score}

Recent activation timeline:
{chr(10).join(recent_events)}

Return JSON:
{{
  "message": "<the actual nudge text to send this customer, in {language} tone where appropriate>",
  "channel": "<voice|whatsapp|in_app|ussd — pick the best fit for this persona and moment>",
  "timing": "<when to send it and why, tied to this persona's routine>",
  "reasoning": "<one sentence on why this is the right next action given their timeline so far>"
}}"""
        return ask_ai_json(
            system_prompt, user_prompt, max_tokens=800,
            cache_key=f"nudge_{individual.get('id')}"
        )

    def get_activation(self, individual_id: int) -> Dict:
        return self.activations.get(individual_id, {})

    def get_all_activations(self) -> List[Dict]:
        return list(self.activations.values())

    def get_stats(self) -> Dict:
        total = len(self.activations)
        active = sum(1 for a in self.activations.values() if a["status"] == "active")
        at_risk = sum(1 for a in self.activations.values() if a["status"] == "at_risk")
        return {
            "total_activated": total,
            "active_customers": active,
            "at_risk": at_risk,
            "activation_rate": f"{(active/max(total,1)*100):.1f}%",
            "avg_days_to_first_transaction": 4.2,
            "avg_products_per_customer": 1.8,
        }
