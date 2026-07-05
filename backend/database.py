from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prism.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Territory(Base):
    __tablename__ = "territories"
    id = Column(Integer, primary_key=True, index=True)
    pincode = Column(String, unique=True, index=True)
    district = Column(String)
    state = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    opportunity_score = Column(Float)
    upi_density = Column(Float)
    telecom_penetration = Column(Float)
    dbt_disbursement = Column(Float)
    agricultural_activity = Column(Float)
    gst_registrations = Column(Integer)
    infrastructure_score = Column(Float)
    unbanked_population = Column(Integer)
    total_population = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Individual(Base):
    __tablename__ = "individuals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    pincode = Column(String)
    district = Column(String)
    phone = Column(String)
    language = Column(String)
    persona_type = Column(String)  # farmer, gig_worker, kirana, first_timer, nri
    financial_readiness_score = Column(Float)
    income_estimate = Column(Float)
    has_bank_account = Column(Boolean, default=False)
    has_smartphone = Column(Boolean)
    dbt_recipient = Column(Boolean)
    upi_active = Column(Boolean)
    occupation = Column(String)
    preferred_channel = Column(String)  # voice, whatsapp, ussd, in_app
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime, nullable=True)
    status = Column(String, default="identified")  # identified, engaged, onboarding, active, dormant
    created_at = Column(DateTime, default=datetime.utcnow)

class Engagement(Base):
    __tablename__ = "engagements"
    id = Column(Integer, primary_key=True, index=True)
    individual_id = Column(Integer, index=True)
    channel = Column(String)
    language = Column(String)
    message_content = Column(Text)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    response_received = Column(Boolean, default=False)
    response_content = Column(Text, nullable=True)
    response_at = Column(DateTime, nullable=True)
    conversion = Column(Boolean, default=False)
    compliance_cleared = Column(Boolean, default=True)
    agent_id = Column(String)

class Activation(Base):
    __tablename__ = "activations"
    id = Column(Integer, primary_key=True, index=True)
    individual_id = Column(Integer, index=True)
    account_opened_at = Column(DateTime)
    first_transaction_at = Column(DateTime, nullable=True)
    days_to_first_transaction = Column(Integer, nullable=True)
    products_adopted = Column(JSON, default=list)
    nudges_sent = Column(Integer, default=0)
    activation_score = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending, active, dormant
    day = Column(Integer, default=0)
    events = Column(JSON, default=list)

class ConsentRecord(Base):
    __tablename__ = "consent_records"
    id = Column(Integer, primary_key=True, index=True)
    individual_id = Column(Integer, index=True)
    consent_type = Column(String)
    consent_method = Column(String)  # missed_call, voice_confirmation, digital
    timestamp = Column(DateTime, default=datetime.utcnow)
    purpose = Column(String)
    data_categories = Column(JSON)
    valid_until = Column(DateTime)
    revoked = Column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_trail"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    layer = Column(String)
    agent = Column(String)
    action = Column(String)
    individual_id = Column(Integer, nullable=True)
    data_accessed = Column(String, nullable=True)
    compliance_status = Column(String)  # passed, flagged, blocked
    rbi_check = Column(Boolean, default=True)
    dpdp_check = Column(Boolean, default=True)
    details = Column(Text, nullable=True)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
