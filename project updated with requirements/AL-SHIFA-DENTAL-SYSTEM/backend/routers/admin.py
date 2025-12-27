# backend/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
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
    Get admin dashboard statistics.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get counts
    total_users = db.query(models.User).count()
    total_doctors = db.query(models.Doctor).count()
    total_patients = db.query(models.Patient).count()
    total_hospitals = db.query(models.Hospital).count()
    
    # Get pending verifications
    pending_doctors = db.query(models.Doctor).filter(
        models.Doctor.is_verified == False
    ).count()
    
    pending_hospitals = db.query(models.Hospital).filter(
        models.Hospital.is_verified == False
    ).count()
    
    return {
        "total_users": total_users,
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_hospitals": total_hospitals,
        "pending_doctor_verifications": pending_doctors,
        "pending_hospital_verifications": pending_hospitals
    }


@router.get("/kyc/doctors")
def get_doctors_by_kyc_status(
    status: Optional[str] = "pending",
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get doctors filtered by KYC verification status.
    status: pending (not verified), approved (verified), all
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(models.Doctor)
    
    if status == "pending":
        query = query.filter(models.Doctor.is_verified == False)
    elif status == "approved":
        query = query.filter(models.Doctor.is_verified == True)
    
    doctors = query.all()
    
    result = []
    for doctor in doctors:
        user = db.query(models.User).filter(models.User.id == doctor.user_id).first()
        hospital = db.query(models.Hospital).filter(
            models.Hospital.id == doctor.hospital_id
        ).first()
        
        result.append({
            "id": str(doctor.id),
            "user_id": str(doctor.user_id),
            "name": user.full_name if user else "Unknown",
            "email": user.email if user else "Unknown",
            "specialization": doctor.specialization,
            "license_number": doctor.license_number,
            "hospital": hospital.name if hospital else "Unknown",
            "is_verified": doctor.is_verified,
            "verified_at": doctor.verified_at.isoformat() if doctor.verified_at else None,
            "created_at": user.created_at.isoformat() if user else None
        })
    
    return result


@router.put("/kyc/doctors/{doctor_id}/approve")
def approve_doctor(
    doctor_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve a doctor's KYC verification.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    if doctor.is_verified:
        raise HTTPException(status_code=400, detail="Doctor is already verified")
    
    # Update verification status
    doctor.is_verified = True
    doctor.verified_by_admin_id = current_user.id
    doctor.verified_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {
        "message": "Doctor approved successfully",
        "doctor_id": str(doctor.id)
    }


@router.put("/kyc/doctors/{doctor_id}/reject")
def reject_doctor(
    doctor_id: str,
    reason: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject a doctor's KYC verification.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # For rejection, we could add a rejection_reason field or handle it differently
    # For now, just keep is_verified as False and log the action
    doctor.is_verified = False
    
    db.commit()
    
    return {
        "message": "Doctor rejected",
        "doctor_id": str(doctor.id),
        "reason": reason
    }


@router.get("/kyc/organizations")
def get_organizations_by_kyc_status(
    status: Optional[str] = "pending",
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get hospitals/organizations filtered by KYC verification status.
    status: pending (not verified), approved (verified), all
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(models.Hospital)
    
    if status == "pending":
        query = query.filter(models.Hospital.is_verified == False)
    elif status == "approved":
        query = query.filter(models.Hospital.is_verified == True)
    
    hospitals = query.all()
    
    result = []
    for hospital in hospitals:
        result.append({
            "id": str(hospital.id),
            "name": hospital.name,
            "address": hospital.address,
            "city": hospital.city,
            "phone": hospital.phone,
            "email": hospital.email,
            "license_number": hospital.license_number,
            "is_verified": hospital.is_verified,
            "verified_at": hospital.verified_at.isoformat() if hospital.verified_at else None,
            "rejection_reason": hospital.rejection_reason,
            "created_at": hospital.created_at.isoformat() if hospital.created_at else None
        })
    
    return result


@router.put("/kyc/organizations/{hospital_id}/approve")
def approve_organization(
    hospital_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve a hospital/organization's KYC verification.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    hospital = db.query(models.Hospital).filter(
        models.Hospital.id == hospital_id
    ).first()
    
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    if hospital.is_verified:
        raise HTTPException(status_code=400, detail="Hospital is already verified")
    
    # Update verification status
    hospital.is_verified = True
    hospital.verified_by_admin_id = current_user.id
    hospital.verified_at = datetime.now(timezone.utc)
    hospital.rejection_reason = None
    
    db.commit()
    
    return {
        "message": "Hospital approved successfully",
        "hospital_id": str(hospital.id)
    }


@router.put("/kyc/organizations/{hospital_id}/reject")
def reject_organization(
    hospital_id: str,
    reason: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject a hospital/organization's KYC verification.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    hospital = db.query(models.Hospital).filter(
        models.Hospital.id == hospital_id
    ).first()
    
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Update rejection status
    hospital.is_verified = False
    hospital.rejection_reason = reason
    
    db.commit()
    
    return {
        "message": "Hospital rejected",
        "hospital_id": str(hospital.id),
        "reason": reason
    }


@router.get("/users")
def get_all_users(
    role: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all users with optional role filter.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(models.User)
    
    if role:
        query = query.filter(models.User.role == role)
    
    users = query.all()
    
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat()
        }
        for u in users
    ]
