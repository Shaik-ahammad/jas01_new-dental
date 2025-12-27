from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

# --- ENUMS (For Strict Typing) ---
# Define these in your codebase or keep as strings if DB doesn't support ENUM types easily
# Roles: 'admin', 'doctor', 'patient', 'hospital_admin'
# Status: 'scheduled', 'completed', 'cancelled', 'no_show'

class User(Base):
    """
    Central Authentication Table (RBAC)
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # doctor, patient, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    patient_profile = relationship("Patient", back_populates="user", uselist=False)


class Hospital(Base):
    """
    Organization / Tenant Entity
    Merged 'Organization' (Ver B) with 'Hospital' (Ver A)
    """
    __tablename__ = "hospitals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False)
    contact_number = Column(String)
    
    # KYC & Verification (From Ver B)
    license_number = Column(String, unique=True, nullable=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    doctors = relationship("Doctor", back_populates="hospital")
    inventory = relationship("Inventory", back_populates="hospital")
    appointments = relationship("Appointment", back_populates="hospital")


class Doctor(Base):
    """
    Doctor Profile & Scheduling Configuration
    Merged Profile info (Ver A) + AI Scheduling Config (Ver B)
    """
    __tablename__ = "doctors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"))
    
    # Professional Info
    specialization = Column(String, nullable=False)
    license_number = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    
    # --- SMART SCHEDULING CONFIG (From Ver B) ---
    # These fields control how the AI Agents book slots
    slot_duration = Column(Integer, default=30)  # Minutes per patient
    break_duration = Column(Integer, default=5)  # Minutes between slots (if interleaved)
    work_start_time = Column(String, default="09:00") # "HH:MM" 24hr format
    work_end_time = Column(String, default="17:00")   # "HH:MM" 24hr format
    
    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    hospital = relationship("Hospital", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")


class Patient(Base):
    """
    Patient Profile
    """
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    
    # Demographics
    age = Column(Integer)
    gender = Column(String)
    medical_history_summary = Column(Text, nullable=True) # For AI Context
    
    # Relationships
    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient")


class Appointment(Base):
    """
    Booking Entity
    Upgraded to use DateTime ranges (Ver B) for better overlap logic
    """
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Linkages
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"))
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"))
    
    # Time Management (Upgrade: DateTime allows timezone handling)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    
    status = Column(String, default="scheduled") # scheduled, completed, cancelled
    reason = Column(String, nullable=True)
    ai_notes = Column(Text, nullable=True) # Summary from AI Chatbot
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    hospital = relationship("Hospital", back_populates="appointments")


class Inventory(Base):
    """
    Resource Management (Preserved from Ver A)
    """
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"))
    
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    unit = Column(String, default="pcs") # e.g., pcs, boxes, ml
    status = Column(String, default="Good") # Good, Low, Critical
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    hospital = relationship("Hospital", back_populates="inventory")