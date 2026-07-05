import pandas as pd
import numpy as np
from faker import Faker
import random
import json
from datetime import datetime, timedelta
import sys
sys.path.append('/home/claude/prism/backend')

fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

VARANASI_PINCODES = [
    {"pincode": "221001", "area": "Varanasi City", "lat": 25.3176, "lng": 82.9739, "rural": False, "dbt_level": 0.4, "telecom": 0.75, "agri": 0.2},
    {"pincode": "221002", "area": "Sigra", "lat": 25.3100, "lng": 82.9800, "rural": False, "dbt_level": 0.35, "telecom": 0.72, "agri": 0.15},
    {"pincode": "221003", "area": "Lanka", "lat": 25.2677, "lng": 82.9913, "rural": False, "dbt_level": 0.3, "telecom": 0.80, "agri": 0.1},
    {"pincode": "221005", "area": "Cantt Area", "lat": 25.2993, "lng": 82.9609, "rural": False, "dbt_level": 0.25, "telecom": 0.85, "agri": 0.05},
    {"pincode": "221007", "area": "Sarnath", "lat": 25.3712, "lng": 83.0243, "rural": True, "dbt_level": 0.65, "telecom": 0.45, "agri": 0.6},
    {"pincode": "221010", "area": "Cholapur", "lat": 25.2100, "lng": 82.8900, "rural": True, "dbt_level": 0.75, "telecom": 0.35, "agri": 0.8},
    {"pincode": "221011", "area": "Arajiline", "lat": 25.1800, "lng": 82.8500, "rural": True, "dbt_level": 0.80, "telecom": 0.30, "agri": 0.85},
    {"pincode": "221104", "area": "Pindra", "lat": 25.4200, "lng": 83.1100, "rural": True, "dbt_level": 0.70, "telecom": 0.40, "agri": 0.75},
    {"pincode": "221105", "area": "Harahua", "lat": 25.4500, "lng": 83.0500, "rural": True, "dbt_level": 0.72, "telecom": 0.38, "agri": 0.78},
    {"pincode": "221106", "area": "Kashi Vidyapeeth", "lat": 25.2500, "lng": 82.9200, "rural": False, "dbt_level": 0.45, "telecom": 0.68, "agri": 0.25},
    {"pincode": "221108", "area": "Baragaon", "lat": 25.3800, "lng": 82.8800, "rural": True, "dbt_level": 0.78, "telecom": 0.32, "agri": 0.82},
    {"pincode": "221112", "area": "Sewapuri", "lat": 25.2300, "lng": 83.1200, "rural": True, "dbt_level": 0.82, "telecom": 0.28, "agri": 0.88},
]

LANGUAGES = {
    "221001": "Hindi", "221002": "Hindi", "221003": "Hindi",
    "221005": "Hindi", "221007": "Bhojpuri", "221010": "Bhojpuri",
    "221011": "Bhojpuri", "221104": "Bhojpuri", "221105": "Bhojpuri",
    "221106": "Hindi", "221108": "Bhojpuri", "221112": "Bhojpuri",
}

PERSONA_WEIGHTS = {
    "rural": {"farmer": 0.45, "gig_worker": 0.10, "kirana": 0.25, "first_timer": 0.15, "nri": 0.05},
    "urban": {"farmer": 0.05, "gig_worker": 0.35, "kirana": 0.20, "first_timer": 0.25, "nri": 0.15},
}

OCCUPATIONS = {
    "farmer": ["Rice farmer", "Wheat farmer", "Vegetable grower", "Dairy farmer", "Sugarcane farmer"],
    "gig_worker": ["Zomato delivery", "Swiggy delivery", "Ola driver", "Auto rickshaw driver", "Daily wage worker"],
    "kirana": ["Kirana store owner", "Tea stall owner", "Vegetable vendor", "Medical shop owner", "Cloth merchant"],
    "first_timer": ["Student", "Private sector employee", "Newly employed", "Apprentice", "Shop assistant"],
    "nri": ["NRI - Gulf", "NRI - UK", "NRI - USA", "NRI - Canada", "NRI - Australia"],
}

def calculate_financial_readiness(pincode_data, persona, age, has_smartphone, upi_active, dbt_recipient, income):
    score = 0
    score += (1 - pincode_data["dbt_level"]) * 20
    score += pincode_data["telecom"] * 15
    if persona == "farmer":
        score += 25 if pincode_data["agri"] > 0.6 else 15
    elif persona == "gig_worker":
        score += 30 if upi_active else 10
    elif persona == "kirana":
        score += 28
    elif persona == "first_timer":
        score += 22
    elif persona == "nri":
        score += 35
    if 22 <= age <= 45:
        score += 10
    elif 46 <= age <= 60:
        score += 7
    else:
        score += 4
    if has_smartphone:
        score += 8
    if upi_active:
        score += 7
    if dbt_recipient:
        score += 5
    if income > 15000:
        score += 10
    elif income > 8000:
        score += 6
    else:
        score += 3
    noise = random.uniform(-5, 5)
    return min(100, max(10, score + noise))

def get_preferred_channel(persona, has_smartphone, pincode_data):
    if persona == "nri":
        return "whatsapp"
    if not has_smartphone or pincode_data["telecom"] < 0.35:
        return "ussd"
    if persona == "farmer" and pincode_data["rural"]:
        return "voice"
    if persona == "gig_worker":
        return "whatsapp"
    if persona == "kirana":
        return random.choice(["whatsapp", "voice"])
    return random.choice(["whatsapp", "voice", "in_app"])

def generate_synthetic_individuals(n=500):
    individuals = []
    per_pincode = n // len(VARANASI_PINCODES)

    for pincode_data in VARANASI_PINCODES:
        pincode = pincode_data["pincode"]
        is_rural = pincode_data["rural"]
        weights = PERSONA_WEIGHTS["rural" if is_rural else "urban"]
        persona_types = list(weights.keys())
        persona_probs = list(weights.values())

        count = per_pincode + (n % len(VARANASI_PINCODES) if pincode_data == VARANASI_PINCODES[-1] else 0)

        for _ in range(count):
            persona = random.choices(persona_types, persona_probs)[0]
            age = random.randint(18, 65)
            gender = random.choice(["Male", "Female", "Male", "Male"])
            has_smartphone = random.random() < pincode_data["telecom"]
            upi_active = random.random() < (0.6 if has_smartphone else 0.1)
            dbt_recipient = random.random() < pincode_data["dbt_level"]

            if persona == "farmer":
                income = random.randint(4000, 20000)
            elif persona == "gig_worker":
                income = random.randint(8000, 25000)
            elif persona == "kirana":
                income = random.randint(15000, 60000)
            elif persona == "first_timer":
                income = random.randint(6000, 30000)
            else:
                income = random.randint(30000, 150000)

            readiness_score = calculate_financial_readiness(
                pincode_data, persona, age, has_smartphone, upi_active, dbt_recipient, income
            )

            channel = get_preferred_channel(persona, has_smartphone, pincode_data)
            language = LANGUAGES.get(pincode, "Hindi")
            occupation = random.choice(OCCUPATIONS[persona])

            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)

            individual = {
                "name": fake.name(),
                "age": age,
                "gender": gender,
                "pincode": pincode,
                "district": "Varanasi",
                "phone": f"+91{random.randint(7000000000, 9999999999)}",
                "language": language,
                "persona_type": persona,
                "financial_readiness_score": round(readiness_score, 2),
                "income_estimate": income,
                "has_bank_account": False,
                "has_smartphone": has_smartphone,
                "dbt_recipient": dbt_recipient,
                "upi_active": upi_active,
                "occupation": occupation,
                "preferred_channel": channel,
                "consent_given": False,
                "status": "identified",
                "latitude": pincode_data["lat"] + lat_offset,
                "longitude": pincode_data["lng"] + lng_offset,
                "area": pincode_data["area"],
            }
            individuals.append(individual)

    return sorted(individuals, key=lambda x: x["financial_readiness_score"], reverse=True)

def generate_territory_data():
    territories = []
    for p in VARANASI_PINCODES:
        unbanked = int(random.uniform(0.3, 0.75) * random.randint(8000, 45000))
        total = unbanked + random.randint(5000, 20000)
        opportunity = (
            p["dbt_level"] * 30 +
            (1 - p["telecom"]) * 20 +
            p["agri"] * 25 +
            (0.7 if p["rural"] else 0.3) * 25
        )
        territories.append({
            "pincode": p["pincode"],
            "district": "Varanasi",
            "state": "Uttar Pradesh",
            "latitude": p["lat"],
            "longitude": p["lng"],
            "opportunity_score": round(min(100, opportunity), 2),
            "upi_density": round(p["telecom"] * 0.7, 2),
            "telecom_penetration": p["telecom"],
            "dbt_disbursement": p["dbt_level"],
            "agricultural_activity": p["agri"],
            "gst_registrations": random.randint(50, 800),
            "infrastructure_score": round(p["telecom"] * 0.8 + random.uniform(0.1, 0.3), 2),
            "unbanked_population": unbanked,
            "total_population": total,
            "area_name": p["area"],
            "is_rural": p["rural"],
        })
    return territories

def generate_activation_timeline(individual):
    events = []
    base_date = datetime.now() - timedelta(days=random.randint(10, 85))
    events.append({"day": 0, "event": "Account opened", "type": "milestone", "date": base_date.strftime("%Y-%m-%d")})

    if individual["financial_readiness_score"] > 70:
        days_to_first = random.randint(1, 5)
    elif individual["financial_readiness_score"] > 50:
        days_to_first = random.randint(3, 10)
    else:
        days_to_first = random.randint(7, 20)

    if days_to_first > 3:
        events.append({"day": 3, "event": "No transaction detected — nudge sent in " + individual["language"], "type": "nudge", "date": (base_date + timedelta(days=3)).strftime("%Y-%m-%d")})

    events.append({"day": days_to_first, "event": "First UPI transaction ₹" + str(random.randint(50, 500)), "type": "milestone", "date": (base_date + timedelta(days=days_to_first)).strftime("%Y-%m-%d")})

    if individual["persona_type"] in ["kirana", "first_timer"]:
        events.append({"day": 15, "event": "FD suggestion sent — ₹5000 idle balance detected", "type": "suggestion", "date": (base_date + timedelta(days=15)).strftime("%Y-%m-%d")})
    if individual["persona_type"] == "farmer":
        events.append({"day": 20, "event": "Kisan Credit Card offer sent", "type": "suggestion", "date": (base_date + timedelta(days=20)).strftime("%Y-%m-%d")})
    if individual["persona_type"] == "gig_worker":
        events.append({"day": 10, "event": "UPI merchant QR code suggested", "type": "suggestion", "date": (base_date + timedelta(days=10)).strftime("%Y-%m-%d")})

    events.append({"day": 30, "event": "30-day financial literacy journey completed", "type": "milestone", "date": (base_date + timedelta(days=30)).strftime("%Y-%m-%d")})
    events.append({"day": 60, "event": "Second product adopted", "type": "milestone", "date": (base_date + timedelta(days=60)).strftime("%Y-%m-%d")})
    events.append({"day": 90, "event": "Active customer — activation complete", "type": "success", "date": (base_date + timedelta(days=90)).strftime("%Y-%m-%d")})

    return events

if __name__ == "__main__":
    print("Generating synthetic data...")
    individuals = generate_synthetic_individuals(500)
    territories = generate_territory_data()
    print(f"Generated {len(individuals)} individuals across {len(territories)} territories")
    print(f"Top lead: {individuals[0]['name']} - Score: {individuals[0]['financial_readiness_score']}")
    import os
    out_dir = os.path.join(os.path.dirname(__file__), 'synthetic')
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'individuals.json'), 'w') as f:
        json.dump(individuals, f, indent=2, default=str)
    with open(os.path.join(out_dir, 'territories.json'), 'w') as f:
        json.dump(territories, f, indent=2, default=str)
    print("Data saved successfully")
