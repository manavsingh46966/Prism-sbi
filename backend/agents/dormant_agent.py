import random
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ai_client import ask_ai_json, is_ai_enabled

DORMANCY_REASONS = {
    "no_use_case": "No relevant product found at time of opening",
    "friction": "Too much friction in app/branch usage",
    "product_mismatch": "Wrong product recommended initially",
    "income_irregular": "Irregular income, unsure how to use account",
    "literacy": "Low digital/financial literacy",
    "competitor": "Moved to competitor offering",
}

REACTIVATION_OFFERS = {
    "farmer": [
        {"offer": "Kisan Credit Card — pre-approved ₹50,000 limit", "reason": "Seasonal credit need detected"},
        {"offer": "PM Fasal Bima Yojana enrollment", "reason": "Crop insurance eligibility identified"},
        {"offer": "Zero-balance upgrade with DBT direct link", "reason": "DBT payments not linked to SBI account"},
    ],
    "gig_worker": [
        {"offer": "Auto-sweep FD — idle balance earns 6.5%", "reason": "Income sitting idle for 60+ days"},
        {"offer": "Personal accident cover ₹2 lakh", "reason": "Gig workers lack insurance coverage"},
        {"offer": "UPI merchant QR — accept payments instantly", "reason": "Cash-heavy transaction pattern detected"},
    ],
    "kirana": [
        {"offer": "Business overdraft ₹1 lakh — instant approval", "reason": "GST filings show growing business"},
        {"offer": "SBI SME loan pre-approval", "reason": "3+ years business history on file"},
        {"offer": "Current account upgrade — lower charges", "reason": "High transaction volume on savings account"},
    ],
    "first_timer": [
        {"offer": "SBI Yono app onboarding — 5 min setup", "reason": "Account never linked to mobile banking"},
        {"offer": "Recurring deposit ₹500/month — start small", "reason": "No savings product adopted"},
        {"offer": "Education loan eligibility check", "reason": "Age 18-25, student profile detected"},
    ],
    "nri": [
        {"offer": "NRE account conversion — tax-free returns", "reason": "Foreign remittance detected, wrong account type"},
        {"offer": "NRI home loan — property in India", "reason": "Real estate inquiry signals detected"},
        {"offer": "Forex card — best rates guaranteed", "reason": "Frequent international travel pattern"},
    ],
}

def generate_dormant_accounts(n: int = 200) -> List[Dict]:
    from faker import Faker
    fake = Faker('en_IN')
    random.seed(99)

    personas = ["farmer", "gig_worker", "kirana", "first_timer", "nri"]
    languages = ["Hindi", "Bhojpuri", "Hindi", "Hindi", "English"]
    accounts = []

    for i in range(n):
        persona = random.choice(personas)
        lang_idx = personas.index(persona)
        dormant_since = datetime.now() - timedelta(days=random.randint(180, 900))
        last_txn = dormant_since + timedelta(days=random.randint(1, 30))
        reason_key = random.choice(list(DORMANCY_REASONS.keys()))

        reactivation_score = random.uniform(30, 95)
        if persona in ["kirana", "gig_worker"]:
            reactivation_score = min(95, reactivation_score + 15)

        accounts.append({
            "id": 5000 + i,
            "name": fake.name(),
            "account_number": f"SBI{random.randint(10000000000, 99999999999)}",
            "persona_type": persona,
            "language": languages[lang_idx],
            "phone": f"+91{random.randint(7000000000, 9999999999)}",
            "dormant_since": dormant_since.strftime("%Y-%m-%d"),
            "last_transaction": last_txn.strftime("%Y-%m-%d"),
            "days_dormant": (datetime.now() - dormant_since).days,
            "account_balance": round(random.uniform(0, 5000), 2),
            "dormancy_reason": reason_key,
            "dormancy_reason_label": DORMANCY_REASONS[reason_key],
            "reactivation_score": round(reactivation_score, 1),
            "reactivation_offer": random.choice(REACTIVATION_OFFERS[persona]),
            "preferred_channel": random.choice(["voice", "whatsapp", "sms"]),
            "status": "dormant",
            "consent_on_file": True,  # Already consented at account opening
            "kyc_complete": True,      # Already KYC done
        })

    return sorted(accounts, key=lambda x: x["reactivation_score"], reverse=True)


class DormantRecoveryAgent:
    def __init__(self):
        self.accounts = generate_dormant_accounts(200)
        self.reactivations = []

    def get_all(self, persona: str = None, min_score: float = 0, limit: int = 100) -> List[Dict]:
        results = self.accounts
        if persona and persona != "all":
            results = [a for a in results if a["persona_type"] == persona]
        results = [a for a in results if a["reactivation_score"] >= min_score]
        return results[:limit]

    def get_by_id(self, account_id: int) -> Dict:
        for a in self.accounts:
            if a["id"] == account_id:
                return a
        return None

    def trigger_reactivation(self, account_id: int) -> Dict:
        account = self.get_by_id(account_id)
        if not account:
            return {"error": "Account not found"}

        channel = account["preferred_channel"]
        language = account["language"]
        persona = account["persona_type"]
        offer = account["reactivation_offer"]

        ai_result = self._ai_reactivation_message(account, offer)

        if ai_result and ai_result.get("message"):
            msg = ai_result["message"]
            ai_generated = True
            agent_mode = "live_agentic_ai"
            reasoning = ai_result.get("reasoning")
        else:
            fallback_messages = {
                "farmer": {
                    "Hindi": f"Namaste! Aapka SBI khata {account['days_dormant']} din se inactive hai. {offer['offer']} — abhi activate karein.",
                    "Bhojpuri": f"Pranam! Aapan SBI khata {account['days_dormant']} din se band ba. {offer['offer']} — abhi shuru karil.",
                },
                "gig_worker": {"Hindi": f"Hello! Aapka SBI account inactive hai. {offer['offer']} — sirf 2 minute mein reactivate karein."},
                "kirana": {"Hindi": f"Namaskar! Aapka business grow kar raha hai — SBI {offer['offer']} offer kar raha hai. Aaj hi activate karein."},
                "first_timer": {"Hindi": f"Hi! Aapka SBI account abhi bhi active ho sakta hai. {offer['offer']} — free mein shuru karein."},
                "nri": {"English": f"Dear Customer, your SBI account has been inactive. We have a special offer: {offer['offer']}. Reactivate today."},
            }
            msg = (fallback_messages.get(persona, {}).get(language)
                   or fallback_messages.get(persona, {}).get("Hindi", f"Reactivate your SBI account — {offer['offer']}"))
            ai_generated = False
            agent_mode = "rule_based_fallback"
            reasoning = None

        result = {
            "id": f"REACT{random.randint(10000, 99999)}",
            "account_id": account_id,
            "account_number": account["account_number"],
            "customer_name": account["name"],
            "channel": channel,
            "language": language,
            "message": msg,
            "offer": offer,
            "status": "reactivation_triggered",
            "triggered_at": datetime.utcnow().isoformat(),
            "consent_required": False,  # Already on file
            "kyc_required": False,       # Already complete
            "estimated_response": "48 hours",
            "cost": "₹12",  # vs ₹1200 for new acquisition
            "demo_note": f"Reactivation via {channel} — consent + KYC already on file. Zero friction.",
            "ai_generated": ai_generated,
            "agent_mode": agent_mode,
            "agent_reasoning": reasoning,
        }

        self.reactivations.append(result)
        return result

    def _ai_reactivation_message(self, account: Dict, offer: Dict) -> Dict:
        """
        Agentic step: Claude writes the actual reactivation outreach,
        explaining WHY this dormant customer likely went quiet (using the
        recorded dormancy_reason as ground truth) and crafting a message
        that speaks to that specific reason — not a generic "come back" ad.
        """
        if not is_ai_enabled():
            return None

        system_prompt = (
            "You are PRISM's Dormant Recovery Agent for SBI. You are re-engaging an "
            "existing account holder (KYC and consent already on file, so this is low-friction) "
            "who has gone inactive. Write a message that acknowledges why they likely went quiet "
            "and offers something that actually addresses that reason — never a generic reminder."
        )
        user_prompt = f"""Dormant account:
Customer: {account.get('name')}
Persona: {account.get('persona_type')}
Language: {account.get('language')}
Days dormant: {account.get('days_dormant')}
Dormancy reason: {account.get('dormancy_reason_label')}
Account balance: Rs {account.get('account_balance')}
Channel: {account.get('preferred_channel')}
Reactivation offer on file: {offer.get('offer')} — {offer.get('reason')}

Return JSON:
{{
  "message": "<the actual outreach message in {account.get('language')}, addressing the specific dormancy reason and offer>",
  "reasoning": "<one sentence on why this message should work for this specific dormancy reason>"
}}"""
        return ask_ai_json(
            system_prompt, user_prompt, max_tokens=800,
            cache_key=f"reactivate_{account.get('id')}"
        )

    def get_reactivation_journey(self, account_id: int) -> Dict:
        account = self.get_by_id(account_id)
        if not account:
            return {}

        base = datetime.now()
        return {
            "account_id": account_id,
            "customer_name": account["name"],
            "journey": [
                {"day": 0, "action": f"Reactivation offer sent via {account['preferred_channel']}", "type": "outreach", "icon": "📨"},
                {"day": 1, "action": "Follow-up if no response", "type": "nudge", "icon": "🔔"},
                {"day": 3, "action": "BC agent visit if rural + no response", "type": "escalation", "icon": "📍"},
                {"day": 5, "action": "Account reactivated — first transaction guided", "type": "milestone", "icon": "✅"},
                {"day": 10, "action": "Second product offer based on persona", "type": "upsell", "icon": "⭐"},
                {"day": 30, "action": "Fully active — moved to retention program", "type": "success", "icon": "🏆"},
            ],
            "advantage": "No KYC needed. No new consent needed. Cost ₹12 vs ₹1,200 for new acquisition.",
        }

    def get_stats(self) -> Dict:
        total = len(self.accounts)
        high_priority = len([a for a in self.accounts if a["reactivation_score"] > 70])
        total_balance = sum(a["account_balance"] for a in self.accounts)
        personas = {}
        for a in self.accounts:
            p = a["persona_type"]
            personas[p] = personas.get(p, 0) + 1

        return {
            "total_dormant_accounts": total,
            "high_priority": high_priority,
            "avg_days_dormant": round(sum(a["days_dormant"] for a in self.accounts) / total),
            "total_idle_balance": f"₹{total_balance:,.0f}",
            "reactivations_triggered": len(self.reactivations),
            "estimated_reactivation_rate": "28%",
            "cost_per_reactivation": "₹12",
            "vs_new_acquisition_cost": "₹1,200",
            "savings_per_customer": "₹1,188",
            "by_persona": personas,
        }
