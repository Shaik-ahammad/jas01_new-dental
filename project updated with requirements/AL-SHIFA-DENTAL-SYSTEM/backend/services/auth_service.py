# backend/services/auth_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status
from typing import Optional
from utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    oauth2_scheme
)
from database import get_db
import models
import schemas


def register_user(user: schemas.UserCreate, db: Session):
    """
    Register a new user with role-based profile creation.
    """
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user with hashed password
    hashed_password = get_password_hash(user.password)
    
    new_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create role-specific profile
    if user.role == "doctor":
        # Get or create a default hospital
        hospital = db.query(models.Hospital).first()
        if not hospital:
            hospital = models.Hospital(
                name="Al-Shifa Main Center",
                location="City Center"
            )
            db.add(hospital)
            db.commit()
            db.refresh(hospital)
        
        doctor_profile = models.Doctor(
            user_id=new_user.id,
            hospital_id=hospital.id,
            specialization=user.specialization or "General Dentist",
            license_number=user.license_number
        )
        db.add(doctor_profile)
        
    elif user.role == "patient":
        patient_profile = models.Patient(
            user_id=new_user.id,
            age=user.age,
            gender=user.gender
        )
        db.add(patient_profile)
    
    db.commit()
    return new_user


def authenticate_user(email: str, password: str, db: Session):
    """
    Authenticate a user by email and password.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to get the current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user
