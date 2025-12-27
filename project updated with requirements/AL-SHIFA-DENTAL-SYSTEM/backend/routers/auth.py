# backend/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from utils.security import create_access_token
from services.auth_service import register_user, authenticate_user, get_current_user
import schemas
import models

router = APIRouter()


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    Supports roles: doctor, patient, admin, organization, staff
    """
    try:
        new_user = register_user(user, db)
        return new_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Registration error: {str(e)}"
        )


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint.
    Returns JWT access token.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }


@router.get("/me")
def get_profile(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile with role-specific details.
    """
    profile_data = {}
    
    if current_user.role == "doctor":
        profile = db.query(models.Doctor).filter(
            models.Doctor.user_id == current_user.id
        ).first()
        if profile:
            profile_data = {
                "specialization": profile.specialization,
                "hospital_id": str(profile.hospital_id),
                "license_number": profile.license_number,
                "schedule_config": {
                    "slot_duration": profile.slot_duration,
                    "break_duration": profile.break_duration,
                    "work_start": profile.work_start_time,
                    "work_end": profile.work_end_time,
                    "available_days": profile.available_days
                }
            }
    elif current_user.role == "patient":
        profile = db.query(models.Patient).filter(
            models.Patient.user_id == current_user.id
        ).first()
        if profile:
            profile_data = {
                "age": profile.age,
                "gender": profile.gender,
                "phone": profile.phone,
                "risk_level": profile.risk_level
            }
    elif current_user.role == "staff":
        profile = db.query(models.Staff).filter(
            models.Staff.user_id == current_user.id
        ).first()
        if profile:
            profile_data = {
                "hospital_id": str(profile.hospital_id),
                "role": profile.role
            }
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "details": profile_data
    }


@router.post("/forgot-password")
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request password reset (placeholder implementation).
    """
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a reset link has been sent"}
    
    # TODO: Implement actual password reset logic with tokens/emails
    return {"message": "If the email exists, a reset link has been sent"}
