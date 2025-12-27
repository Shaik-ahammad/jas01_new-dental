# backend/routers/doctor.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import date, datetime, timedelta
from typing import List, Optional
from database import get_db
from services.auth_service import get_current_user
import schemas
import models

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get doctor dashboard statistics.
    """
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    doctor = db.query(models.Doctor).filter(
        models.Doctor.user_id == current_user.id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    # Get today's appointments
    today = date.today()
    todays_appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor.id,
        func.date(models.Appointment.start_time) == today
    ).all()
    
    # Get total patients count
    total_patients = db.query(models.Appointment.patient_id).filter(
        models.Appointment.doctor_id == doctor.id
    ).distinct().count()
    
    # Calculate revenue (simplified)
    revenue = len(todays_appointments) * 1500
    
    return {
        "today_count": len(todays_appointments),
        "revenue": revenue,
        "active_patients": total_patients,
        "appointments": [
            {
                "id": str(a.id),
                "time": a.start_time.strftime("%H:%M"),
                "status": a.status,
                "patient_id": str(a.patient_id)
            }
            for a in todays_appointments
        ]
    }


@router.get("/schedule-config")
def get_schedule_config(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get doctor's scheduling configuration.
    """
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    doctor = db.query(models.Doctor).filter(
        models.Doctor.user_id == current_user.id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    return {
        "slot_duration": doctor.slot_duration,
        "break_duration": doctor.break_duration,
        "work_start": doctor.work_start_time,
        "work_end": doctor.work_end_time,
        "available_days": doctor.available_days,
        "scheduling_mode": doctor.scheduling_mode
    }


@router.put("/schedule-config")
def update_schedule_config(
    config: schemas.DoctorScheduleConfig,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update doctor's scheduling configuration.
    """
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    doctor = db.query(models.Doctor).filter(
        models.Doctor.user_id == current_user.id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    # Update configuration
    doctor.slot_duration = config.slot_duration
    doctor.break_duration = config.break_duration
    doctor.work_start_time = config.work_start
    doctor.work_end_time = config.work_end
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Schedule configuration updated successfully"
    }


@router.get("/schedule-slots")
def get_schedule_slots(
    date_str: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available time slots for a specific date.
    """
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    doctor = db.query(models.Doctor).filter(
        models.Doctor.user_id == current_user.id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    # Parse date
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Get booked appointments for the date
    booked_appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor.id,
        func.date(models.Appointment.start_time) == target_date
    ).all()
    
    booked_slots = [
        a.start_time.strftime("%H:%M") for a in booked_appointments
    ]
    
    return {
        "date": date_str,
        "booked_slots": booked_slots,
        "work_start": doctor.work_start_time,
        "work_end": doctor.work_end_time,
        "slot_duration": doctor.slot_duration
    }


@router.get("/patients")
def get_patients(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all patients who have appointments with this doctor.
    """
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    doctor = db.query(models.Doctor).filter(
        models.Doctor.user_id == current_user.id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    # Get distinct patients
    patients = db.query(models.Patient).join(
        models.Appointment,
        models.Appointment.patient_id == models.Patient.id
    ).filter(
        models.Appointment.doctor_id == doctor.id
    ).distinct().all()
    
    return [
        {
            "id": str(p.id),
            "user_id": str(p.user_id),
            "gender": p.gender,
            "age": p.age,
            "risk_level": p.risk_level
        }
        for p in patients
    ]


@router.get("/patients/{patient_id}")
def get_patient_detail(
    patient_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific patient.
    """
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get patient user info
    user = db.query(models.User).filter(models.User.id == patient.user_id).first()
    
    # Get appointment history
    appointments = db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient.id
    ).order_by(models.Appointment.start_time.desc()).limit(10).all()
    
    return {
        "id": str(patient.id),
        "full_name": user.full_name if user else "Unknown",
        "email": user.email if user else "Unknown",
        "gender": patient.gender,
        "age": patient.age,
        "phone": patient.phone,
        "risk_level": patient.risk_level,
        "allergies": patient.allergies,
        "medical_conditions": patient.medical_conditions,
        "recent_appointments": [
            {
                "id": str(a.id),
                "date": a.start_time.strftime("%Y-%m-%d"),
                "time": a.start_time.strftime("%H:%M"),
                "status": a.status
            }
            for a in appointments
        ]
    }
