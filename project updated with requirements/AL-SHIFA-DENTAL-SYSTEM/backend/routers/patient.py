# backend/routers/patient.py

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
    Get patient dashboard information.
    """
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    
    patient = db.query(models.Patient).filter(
        models.Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    # Get upcoming appointments
    today = datetime.now()
    upcoming_appointments = db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient.id,
        models.Appointment.start_time >= today,
        models.Appointment.status == "scheduled"
    ).order_by(models.Appointment.start_time).limit(5).all()
    
    # Get past appointments count
    past_appointments_count = db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient.id,
        models.Appointment.start_time < today
    ).count()
    
    return {
        "patient_id": str(patient.id),
        "full_name": current_user.full_name,
        "upcoming_appointments": len(upcoming_appointments),
        "past_appointments": past_appointments_count,
        "risk_level": patient.risk_level,
        "next_appointments": [
            {
                "id": str(a.id),
                "date": a.start_time.strftime("%Y-%m-%d"),
                "time": a.start_time.strftime("%H:%M"),
                "doctor_id": str(a.doctor_id),
                "status": a.status
            }
            for a in upcoming_appointments
        ]
    }


@router.get("/appointments")
def get_appointments(
    status: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient's appointments with optional status filter.
    """
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    
    patient = db.query(models.Patient).filter(
        models.Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    query = db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient.id
    )
    
    if status:
        query = query.filter(models.Appointment.status == status)
    
    appointments = query.order_by(models.Appointment.start_time.desc()).all()
    
    result = []
    for appointment in appointments:
        doctor = db.query(models.Doctor).filter(
            models.Doctor.id == appointment.doctor_id
        ).first()
        doctor_user = db.query(models.User).filter(
            models.User.id == doctor.user_id
        ).first() if doctor else None
        
        hospital = db.query(models.Hospital).filter(
            models.Hospital.id == appointment.hospital_id
        ).first()
        
        result.append({
            "id": str(appointment.id),
            "date": appointment.start_time.strftime("%Y-%m-%d"),
            "time": appointment.start_time.strftime("%H:%M"),
            "status": appointment.status,
            "doctor_name": doctor_user.full_name if doctor_user else "Unknown",
            "hospital_name": hospital.name if hospital else "Unknown",
            "reason": appointment.reason_for_visit or appointment.reason
        })
    
    return result


@router.post("/appointments")
def book_appointment(
    appointment: schemas.AppointmentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Book a new appointment.
    """
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    
    patient = db.query(models.Patient).filter(
        models.Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    # Get doctor
    if not appointment.doctor_id:
        raise HTTPException(status_code=400, detail="Doctor ID is required")
    
    doctor = db.query(models.Doctor).filter(
        models.Doctor.id == appointment.doctor_id
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Parse datetime
    try:
        appointment_datetime = datetime.combine(
            appointment.date,
            datetime.strptime(appointment.time, "%H:%M").time()
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
    
    # Calculate end time based on slot duration
    end_time = appointment_datetime + timedelta(minutes=doctor.slot_duration)
    
    # Check for conflicts
    conflict = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor.id,
        models.Appointment.start_time < end_time,
        models.Appointment.end_time > appointment_datetime,
        models.Appointment.status == "scheduled"
    ).first()
    
    if conflict:
        raise HTTPException(status_code=409, detail="Time slot is already booked")
    
    # Create appointment
    new_appointment = models.Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        hospital_id=doctor.hospital_id,
        appointment_date=appointment.date,
        start_time=appointment_datetime,
        end_time=end_time,
        reason_for_visit=appointment.reason,
        status="scheduled"
    )
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    return {
        "id": str(new_appointment.id),
        "message": "Appointment booked successfully",
        "date": appointment.date.strftime("%Y-%m-%d"),
        "time": appointment.time
    }


@router.put("/appointments/{appointment_id}/reschedule")
def reschedule_appointment(
    appointment_id: str,
    new_date: date,
    new_time: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reschedule an existing appointment.
    """
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    
    patient = db.query(models.Patient).filter(
        models.Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.patient_id == patient.id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.status != "scheduled":
        raise HTTPException(
            status_code=400,
            detail="Can only reschedule scheduled appointments"
        )
    
    # Parse new datetime
    try:
        new_datetime = datetime.combine(
            new_date,
            datetime.strptime(new_time, "%H:%M").time()
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
    
    # Get doctor for slot duration
    doctor = db.query(models.Doctor).filter(
        models.Doctor.id == appointment.doctor_id
    ).first()
    
    new_end_time = new_datetime + timedelta(minutes=doctor.slot_duration)
    
    # Check for conflicts
    conflict = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == appointment.doctor_id,
        models.Appointment.id != appointment_id,
        models.Appointment.start_time < new_end_time,
        models.Appointment.end_time > new_datetime,
        models.Appointment.status == "scheduled"
    ).first()
    
    if conflict:
        raise HTTPException(status_code=409, detail="New time slot is already booked")
    
    # Update appointment
    appointment.appointment_date = new_date
    appointment.start_time = new_datetime
    appointment.end_time = new_end_time
    
    db.commit()
    
    return {
        "message": "Appointment rescheduled successfully",
        "new_date": new_date.strftime("%Y-%m-%d"),
        "new_time": new_time
    }


@router.delete("/appointments/{appointment_id}")
def cancel_appointment(
    appointment_id: str,
    reason: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an appointment.
    """
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    
    patient = db.query(models.Patient).filter(
        models.Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.patient_id == patient.id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.status == "cancelled":
        raise HTTPException(status_code=400, detail="Appointment is already cancelled")
    
    # Update appointment status
    appointment.status = "cancelled"
    appointment.cancelled_at = datetime.now()
    appointment.cancellation_reason = reason
    
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}


@router.get("/records")
def get_medical_records(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient's medical records.
    """
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    
    patient = db.query(models.Patient).filter(
        models.Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    # Get patient histories
    histories = db.query(models.PatientHistory).filter(
        models.PatientHistory.patient_id == patient.id
    ).order_by(models.PatientHistory.created_at.desc()).all()
    
    result = []
    for history in histories:
        doctor = db.query(models.Doctor).filter(
            models.Doctor.id == history.doctor_id
        ).first()
        doctor_user = db.query(models.User).filter(
            models.User.id == doctor.user_id
        ).first() if doctor else None
        
        result.append({
            "id": str(history.id),
            "date": history.created_at.strftime("%Y-%m-%d"),
            "doctor_name": doctor_user.full_name if doctor_user else "Unknown",
            "diagnosis": history.diagnosis,
            "treatment": history.treatment_provided,
            "medications": history.medications_prescribed,
            "follow_up": history.follow_up_date.strftime("%Y-%m-%d") if history.follow_up_date else None
        })
    
    return result


@router.get("/doctors")
def browse_doctors(
    specialization: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Browse available doctors.
    """
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(models.Doctor).filter(models.Doctor.is_verified == True)
    
    if specialization:
        query = query.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))
    
    doctors = query.all()
    
    result = []
    for doctor in doctors:
        user = db.query(models.User).filter(models.User.id == doctor.user_id).first()
        hospital = db.query(models.Hospital).filter(
            models.Hospital.id == doctor.hospital_id
        ).first()
        
        result.append({
            "id": str(doctor.id),
            "name": user.full_name if user else "Unknown",
            "specialization": doctor.specialization,
            "hospital": hospital.name if hospital else "Unknown",
            "avg_rating": doctor.avg_rating,
            "total_reviews": doctor.total_reviews
        })
    
    return result
