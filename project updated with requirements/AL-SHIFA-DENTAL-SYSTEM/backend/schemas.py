# backend/schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import date, datetime

# ==========================================================
# 1. SHARED BASES
# ==========================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str  # 'doctor' or 'patient'

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    id: Optional[str] = None
    role: Optional[str] = None

# ==========================================================
# 2. AUTHENTICATION (INPUTS)
# ==========================================================

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserBase):
    password: str
    
    # Doctor Fields
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    hospital_name: Optional[str] = None
    
    # Patient Fields
    age: Optional[int] = None
    gender: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# ==========================================================
# 3. DOCTOR CONFIGURATION (FROM VERSION B)
# ==========================================================

class DoctorScheduleConfig(BaseModel):
    slot_duration: int = Field(default=30, description="Minutes per patient")
    break_duration: int = Field(default=5, description="Minutes between slots")
    work_start: str = Field(default="09:00", description="HH:MM format")
    work_end: str = Field(default="17:00", description="HH:MM format")

class DoctorProfileOut(BaseModel):
    specialization: str
    hospital_name: Optional[str] = None
    license_number: Optional[str] = None
    schedule_config: Optional[DoctorScheduleConfig] = None

# ==========================================================
# 4. APPOINTMENTS (FROM VERSION A)
# ==========================================================

class AppointmentCreate(BaseModel):
    doctor_id: Optional[UUID] = None
    date: date
    time: str # "HH:MM"
    reason: str = "General Checkup"

class AppointmentOut(BaseModel):
    id: UUID
    date: date
    time: str
    status: str
    doctor_name: str
    hospital_name: str
    
    class Config:
        from_attributes = True

# ==========================================================
# 5. USER RESPONSES (OUTPUTS)
# ==========================================================

class UserOut(UserBase):
    id: UUID
    is_active: bool
    details: Optional[Any] = None # Will hold DoctorProfileOut or Patient details

    class Config:
        from_attributes = True

# ==========================================================
# 6. HOSPITAL/ORGANIZATION SCHEMAS
# ==========================================================

class HospitalCreate(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    license_number: Optional[str] = None
    registration_document_url: Optional[str] = None

class HospitalOut(BaseModel):
    id: UUID
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_verified: bool
    license_number: Optional[str] = None
    
    class Config:
        from_attributes = True

# ==========================================================
# 7. PATIENT SCHEMAS
# ==========================================================

class PatientCreate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None

class PatientOut(BaseModel):
    id: UUID
    user_id: UUID
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    risk_level: str
    
    class Config:
        from_attributes = True

# ==========================================================
# 8. INVENTORY SCHEMAS
# ==========================================================

class InventoryCreate(BaseModel):
    item_name: str
    category: Optional[str] = None
    quantity: int = 0
    unit: str = "pcs"
    min_threshold: Optional[int] = None
    max_threshold: Optional[int] = None
    reorder_quantity: Optional[int] = None
    cost_per_unit: Optional[float] = None

class InventoryOut(BaseModel):
    id: UUID
    hospital_id: UUID
    item_name: str
    category: Optional[str] = None
    quantity: int
    unit: str
    status: str
    
    class Config:
        from_attributes = True

# ==========================================================
# 9. STAFF SCHEMAS
# ==========================================================

class StaffCreate(BaseModel):
    user_id: UUID
    hospital_id: UUID
    role: str  # receptionist, nurse, dental_technician
    assigned_doctors: Optional[str] = None
    assigned_shifts: Optional[str] = None

class StaffOut(BaseModel):
    id: UUID
    user_id: UUID
    hospital_id: UUID
    role: str
    
    class Config:
        from_attributes = True