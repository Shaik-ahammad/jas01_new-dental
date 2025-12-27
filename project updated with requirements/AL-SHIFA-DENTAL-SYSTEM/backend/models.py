from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum, Float, Date
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
    role = Column(String, nullable=False)  # admin, doctor, patient, organization, staff
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    patient_profile = relationship("Patient", back_populates="user", uselist=False)
    staff_profile = relationship("Staff", back_populates="user", uselist=False)


class Hospital(Base):
    """
    Organization / Tenant Entity
    Merged 'Organization' (Ver B) with 'Hospital' (Ver A)
    """
    __tablename__ = "hospitals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    location = Column(String, nullable=True)  # Legacy field
    contact_number = Column(String, nullable=True)  # Legacy field
    
    # KYC & Verification
    license_number = Column(String, unique=True, nullable=True)
    registration_document_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verified_by_admin_id = Column(UUID(as_uuid=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    doctors = relationship("Doctor", back_populates="hospital")
    inventory = relationship("Inventory", back_populates="hospital")
    appointments = relationship("Appointment", back_populates="hospital")
    revenues = relationship("Revenue", back_populates="hospital")
    staff = relationship("Staff", back_populates="hospital")


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
    license_document_url = Column(String, nullable=True)
    medical_degree_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verified_by_admin_id = Column(UUID(as_uuid=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Smart Scheduling Configuration
    scheduling_mode = Column(String, default="continuous")  # continuous, interleaved, custom
    slot_duration = Column(Integer, default=30)  # Minutes per patient
    break_duration = Column(Integer, default=5)  # Minutes between slots (if interleaved)
    work_start_time = Column(String, default="09:00")  # "HH:MM" 24hr format
    work_end_time = Column(String, default="17:00")  # "HH:MM" 24hr format
    available_days = Column(String, default="1,2,3,4,5")  # Comma-separated day numbers (1=Monday)
    
    # Google Calendar Integration
    google_calendar_connected = Column(Boolean, default=False)
    google_calendar_id = Column(String, nullable=True)
    
    # Ratings
    avg_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    hospital = relationship("Hospital", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
    patient_histories = relationship("PatientHistory", back_populates="doctor")
    case_trackings = relationship("CaseTracking", back_populates="doctor")
    revenues = relationship("Revenue", back_populates="doctor")


class Patient(Base):
    """
    Patient Profile
    """
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    
    # Demographics
    date_of_birth = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)  # Legacy field
    gender = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    # Medical Information
    allergies = Column(Text, nullable=True)
    medical_conditions = Column(Text, nullable=True)
    medical_history_summary = Column(Text, nullable=True)  # For AI Context
    risk_level = Column(String, default="LOW")  # LOW, MEDIUM, HIGH
    
    # Insurance
    insurance_provider = Column(String, nullable=True)
    insurance_policy_number = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient")
    patient_histories = relationship("PatientHistory", back_populates="patient")
    case_trackings = relationship("CaseTracking", back_populates="patient")
    revenues = relationship("Revenue", back_populates="patient")


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
    
    # Time Management (DateTime allows timezone handling)
    appointment_date = Column(Date, nullable=True)  # Additional date field
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    
    # Status & Details
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled, no_show
    reason_for_visit = Column(String, nullable=True)
    chief_complaint = Column(Text, nullable=True)
    clinical_notes = Column(Text, nullable=True)
    reason = Column(String, nullable=True)  # Legacy field
    ai_notes = Column(Text, nullable=True)  # Summary from AI Chatbot
    
    # Notifications & Confirmations
    patient_confirmed = Column(Boolean, default=False)
    whatsapp_sent = Column(Boolean, default=False)
    
    # Calendar Integration
    google_calendar_event_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    hospital = relationship("Hospital", back_populates="appointments")
    patient_histories = relationship("PatientHistory", back_populates="appointment")
    revenues = relationship("Revenue", back_populates="appointment")


class Inventory(Base):
    """
    Resource Management (Preserved from Ver A)
    """
    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"))
    
    item_name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    quantity = Column(Integer, default=0)
    unit = Column(String, default="pcs")  # e.g., pcs, boxes, ml
    min_threshold = Column(Integer, nullable=True)
    max_threshold = Column(Integer, nullable=True)
    reorder_quantity = Column(Integer, nullable=True)
    cost_per_unit = Column(Float, nullable=True)
    status = Column(String, default="Good")  # Good, Low, Critical
    last_reorder_date = Column(Date, nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hospital = relationship("Hospital", back_populates="inventory")


class PatientHistory(Base):
    """
    Medical History & Treatment Records
    """
    __tablename__ = "patient_histories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"))
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    
    clinical_notes = Column(Text, nullable=True)
    diagnosis = Column(String, nullable=True)
    treatment_provided = Column(String, nullable=True)
    medications_prescribed = Column(Text, nullable=True)  # JSON format
    follow_up_date = Column(Date, nullable=True)
    follow_up_instructions = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="patient_histories")
    doctor = relationship("Doctor", back_populates="patient_histories")
    appointment = relationship("Appointment", back_populates="patient_histories")


class CaseTracking(Base):
    """
    Long-term Treatment Case Tracking
    """
    __tablename__ = "case_trackings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"))
    
    case_type = Column(String, nullable=True)
    status = Column(String, default="Active")  # Active, Completed, On Hold
    start_date = Column(Date, nullable=True)
    expected_end_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    
    # Milestone Tracking
    current_milestone = Column(String, nullable=True)
    next_milestone = Column(String, nullable=True)
    milestone_date = Column(Date, nullable=True)
    
    # Vector DB Integration
    vector_doc_id = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="case_trackings")
    doctor = relationship("Doctor", back_populates="case_trackings")


class Revenue(Base):
    """
    Financial Tracking
    """
    __tablename__ = "revenues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"))
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"))
    
    amount = Column(Float, nullable=False)
    service_type = Column(String, nullable=True)
    insurance_amount = Column(Float, default=0.0)
    patient_amount = Column(Float, default=0.0)
    payment_status = Column(String, default="Pending")  # Pending, Paid, Partial
    payment_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    appointment = relationship("Appointment", back_populates="revenues")
    patient = relationship("Patient", back_populates="revenues")
    doctor = relationship("Doctor", back_populates="revenues")
    hospital = relationship("Hospital", back_populates="revenues")


class Staff(Base):
    """
    Staff Management (Receptionist, Nurse, Dental Technician)
    """
    __tablename__ = "staff"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"))
    
    role = Column(String, nullable=False)  # receptionist, nurse, dental_technician
    assigned_doctors = Column(Text, nullable=True)  # JSON format
    assigned_shifts = Column(Text, nullable=True)  # JSON format
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="staff_profile")
    hospital = relationship("Hospital", back_populates="staff")