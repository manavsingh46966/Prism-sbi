import json
import os
import sys
from typing import List, Dict, Optional
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ai_client import ask_ai_json, is_ai_enabled

class IndividualSignalAgent:
    def __init__(self):
        self.individuals = self._load_individuals()

    def _load_individuals(self):
        base = os.path.join(os.path.dirname(__file__), '..', 'data', 'synthetic', 'individuals.json')
        with open(os.path.abspath(base)) as f:
            data = json.load(f)
        for i, ind in enumerate(data):
            ind["id"] = i + 1
        return data

    def get_all(self, pincode: str = None, persona: str = None, min_score: float = 0, limit: int = 100) -> List[Dict]:
        results = self.individuals
        if pincode:
            results = [i for i in results if i["pincode"] == pincode]
        if persona and persona != "all":
            results = [i for i in results if i["persona_type"] == persona]
        results = [i for i in results if i["financial_readiness_score"] >= min_score]
        return results[:limit]

    def get_by_id(self, individual_id: int) -> Optional[Dict]:
        for ind in self.individuals:
            if ind["id"] == individual_id:
                return ind
        return None

    def get_profile(self, individual_id: int) -> Dict:
        ind = self.get_by_id(individual_id)
        if not ind:
            return {}

        # Rule-based signals are ALWAYS computed first — these come from real
        # (or realistically-correlated synthetic) source data and are the
        # ground truth the AI agent reasons over. The AI layer's job is to
        # interpret them like an analyst would, not to invent facts.
        raw_signals = self._build_signals(ind)
        rule_recommendations = self._build_recommendations(ind)
        rule_engagement_plan = self._build_engagement_plan(ind)
        rule_risk_factors = self._build_risk_factors(ind)

        ai_analysis = self._ai_readiness_analysis(ind, raw_signals)

        if ai_analysis:
            return {
                "individual": ind,
                "signals": raw_signals,
                "recommendations": ai_analysis.get("recommendations", rule_recommendations),
                "engagement_plan": {**rule_engagement_plan, **ai_analysis.get("engagement_plan_overrides", {})},
                "risk_factors": ai_analysis.get("risk_factors", rule_risk_factors),
                "ai_narrative": ai_analysis.get("narrative"),
                "ai_adjusted_score": ai_analysis.get("adjusted_readiness_score", ind["financial_readiness_score"]),
                "ai_generated": True,
                "agent_mode": "live_agentic_ai",
            }

        return {
            "individual": ind,
            "signals": raw_signals,
            "recommendations": rule_recommendations,
            "engagement_plan": rule_engagement_plan,
            "risk_factors": rule_risk_factors,
            "ai_narrative": None,
            "ai_adjusted_score": ind["financial_readiness_score"],
            "ai_generated": False,
            "agent_mode": "rule_based_fallback",
        }

    def _ai_readiness_analysis(self, ind: Dict, raw_signals: List[Dict]) -> Optional[Dict]:
        """
        Agentic reasoning step: an LLM acts as a customer-acquisition analyst,
        reading the individual's real signals (income, DBT status, UPI
        activity, phone type, persona, locale) and producing a genuinely
        reasoned — not templated — readiness assessment, product ranking,
        risk read, and engagement approach. This replaces the old fixed
        priority-1/2/3 product lists and static risk-factor rules for
        anyone whose profile the AI has actually looked at.
        """
        if not is_ai_enabled():
            return None

        system_prompt = (
            "You are PRISM's Individual Signal Agent, an AI analyst inside an SBI "
            "(State Bank of India) customer-acquisition system. You are given real "
            "behavioural and demographic signals for one unbanked/underbanked "
            "individual. Reason like a careful credit/product analyst: weigh the "
            "signals against each other (don't just restate them), decide which "
            "SBI products genuinely fit this person's life circumstances, flag "
            "real onboarding risks, and suggest how PRISM should adjust its "
            "confidence in this lead. Be specific to THIS person, not generic."
        )

        user_prompt = f"""Individual profile:
Name: {ind.get('name')}
Age: {ind.get('age')}
Persona type: {ind.get('persona_type')}
Location (pincode): {ind.get('pincode')}, area: {ind.get('area')}
Language: {ind.get('language')}
Has smartphone: {ind.get('has_smartphone')}
Has existing bank account: {ind.get('has_bank_account')}
DBT (govt transfer) recipient: {ind.get('dbt_recipient')}
UPI active: {ind.get('upi_active')}
Estimated monthly income: Rs {ind.get('income_estimate')}
Rule-engine readiness score (0-100): {ind.get('financial_readiness_score')}
Preferred channel (rule-derived): {ind.get('preferred_channel')}

Detected signals: {json.dumps([s['signal'] for s in raw_signals])}

Return JSON with this exact shape:
{{
  "adjusted_readiness_score": <float 0-100, your own judgement, may differ from the rule-engine score, with reasoning baked into narrative>,
  "narrative": "<2-3 sentence analyst read on this specific lead — why they are or aren't a strong acquisition target right now>",
  "recommendations": [
    {{"product": "<SBI product name>", "reason": "<specific reason tied to THIS person's signals>", "priority": 1}},
    {{"product": "...", "reason": "...", "priority": 2}},
    {{"product": "...", "reason": "...", "priority": 3}}
  ],
  "risk_factors": ["<specific onboarding risk 1>", "<risk 2>"],
  "engagement_plan_overrides": {{"message_preview": "<one short line, in the person's language/dialect if not English, that a real outreach would open with>"}}
}}"""

        return ask_ai_json(
            system_prompt, user_prompt, max_tokens=1400,
            cache_key=f"signal_profile_{ind.get('id')}"
        )

    def _build_signals(self, ind: Dict) -> List[Dict]:
        signals = []
        if ind["dbt_recipient"]:
            signals.append({"signal": "DBT recipient", "source": "DBT Bharat Portal", "strength": "High", "icon": "government"})
        if ind["upi_active"]:
            signals.append({"signal": "Active UPI user — no savings linked", "source": "NPCI aggregate data", "strength": "High", "icon": "payment"})
        if not ind["has_bank_account"]:
            signals.append({"signal": "No formal bank account detected", "source": "Jan Dhan Yojana data", "strength": "High", "icon": "bank"})
        if ind["persona_type"] == "farmer" and ind["pincode"] in ["221007", "221010", "221011", "221104", "221105", "221108", "221112"]:
            signals.append({"signal": "Active in agricultural zone — harvest season", "source": "Agmarknet", "strength": "Medium", "icon": "agriculture"})
        if ind["persona_type"] == "kirana":
            signals.append({"signal": "Business registered, cash-heavy transactions", "source": "GST Portal", "strength": "High", "icon": "business"})
        if ind["persona_type"] == "gig_worker":
            signals.append({"signal": "Regular gig income via UPI — no savings product", "source": "NPCI patterns", "strength": "High", "icon": "gig"})
        if not ind["has_smartphone"]:
            signals.append({"signal": "Feature phone user — USSD channel preferred", "source": "TRAI data", "strength": "Medium", "icon": "phone"})
        return signals

    def _build_recommendations(self, ind: Dict) -> List[Dict]:
        recs = []
        persona = ind["persona_type"]
        if persona == "farmer":
            recs = [
                {"product": "SBI Kisan Savings Account", "reason": "Zero balance, crop loan eligibility", "priority": 1},
                {"product": "Kisan Credit Card", "reason": "Seasonal credit for inputs", "priority": 2},
                {"product": "Pradhan Mantri Fasal Bima", "reason": "Crop insurance via SBI", "priority": 3},
            ]
        elif persona == "gig_worker":
            recs = [
                {"product": "SBI Basic Savings Account", "reason": "Secure gig income, UPI-enabled", "priority": 1},
                {"product": "SBI Recurring Deposit", "reason": "Disciplined savings from gig income", "priority": 2},
                {"product": "SBI Personal Loan", "reason": "Emergency credit for gig workers", "priority": 3},
            ]
        elif persona == "kirana":
            recs = [
                {"product": "SBI Current Account", "reason": "Business transactions, overdraft facility", "priority": 1},
                {"product": "SBI SME Loan", "reason": "Business expansion credit", "priority": 2},
                {"product": "SBI Merchant UPI", "reason": "Digital payment acceptance", "priority": 3},
            ]
        elif persona == "first_timer":
            recs = [
                {"product": "SBI Savings Account", "reason": "First account, full digital access", "priority": 1},
                {"product": "SBI Debit Card", "reason": "Everyday spending, ATM access", "priority": 2},
                {"product": "SBI Fixed Deposit", "reason": "Safe savings for first earners", "priority": 3},
            ]
        elif persona == "nri":
            recs = [
                {"product": "SBI NRE Account", "reason": "Tax-free remittance, repatriable", "priority": 1},
                {"product": "SBI NRO Account", "reason": "Indian income management", "priority": 2},
                {"product": "SBI NRI Home Loan", "reason": "Property investment in India", "priority": 3},
            ]
        return recs

    def _build_engagement_plan(self, ind: Dict) -> Dict:
        channel = ind["preferred_channel"]
        language = ind["language"]
        persona = ind["persona_type"]

        timing_map = {
            "farmer": "7:00 AM - 9:00 AM (before field work)",
            "gig_worker": "9:00 PM - 10:00 PM (after shift)",
            "kirana": "2:00 PM - 4:00 PM (slow business hours)",
            "first_timer": "12:00 PM - 1:00 PM (lunch break)",
            "nri": "8:00 PM - 10:00 PM IST",
        }

        message_map = {
            "farmer": f"Namaste! SBI ka Kisan Savings Account kholen — zero balance, seedha DBT payment",
            "gig_worker": f"Aapki delivery income secure karein — SBI account free mein kholen",
            "kirana": f"Aapke business ke liye SBI Current Account — overdraft bhi milega",
            "first_timer": f"Pehli naukri, pehla bank account — SBI mein free mein kholen",
            "nri": f"Send money home instantly — open your SBI NRE account today",
        }

        return {
            "channel": channel,
            "language": language,
            "optimal_timing": timing_map.get(persona, "10:00 AM - 12:00 PM"),
            "message_preview": message_map.get(persona, "SBI mein khata kholen"),
            "consent_method": "missed_call" if not ind["has_smartphone"] else "digital",
            "fallback_channel": "ussd" if not ind["has_smartphone"] else "voice",
            "bc_dispatch_required": not ind["has_smartphone"] and ind["persona_type"] == "farmer",
        }

    def _build_risk_factors(self, ind: Dict) -> List[str]:
        risks = []
        if ind["age"] > 55:
            risks.append("Older demographic — may need assisted onboarding")
        if not ind["has_smartphone"]:
            risks.append("No smartphone — USSD or BC agent required")
        if ind["financial_readiness_score"] < 40:
            risks.append("Low readiness score — multiple touchpoints needed")
        if ind["language"] == "Bhojpuri":
            risks.append("Vernacular language required — Bhojpuri agent needed")
        return risks

    def get_persona_stats(self) -> Dict:
        stats = {}
        personas = ["farmer", "gig_worker", "kirana", "first_timer", "nri"]
        for p in personas:
            group = [i for i in self.individuals if i["persona_type"] == p]
            stats[p] = {
                "count": len(group),
                "avg_score": round(sum(i["financial_readiness_score"] for i in group) / max(len(group), 1), 1),
                "avg_income": round(sum(i["income_estimate"] for i in group) / max(len(group), 1)),
                "smartphone_pct": round(sum(1 for i in group if i["has_smartphone"]) / max(len(group), 1) * 100, 1),
            }
        return stats
