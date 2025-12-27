# backend/routers/organization.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import date, datetime
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
    Get organization dashboard statistics.
    """
    if current_user.role != "organization":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Get organization profile for current user
    # For now, get first hospital (simplified)
    hospital = db.query(models.Hospital).first()
    
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Get statistics
    total_doctors = db.query(models.Doctor).filter(
        models.Doctor.hospital_id == hospital.id
    ).count()
    
    total_staff = db.query(models.Staff).filter(
        models.Staff.hospital_id == hospital.id
    ).count()
    
    total_appointments = db.query(models.Appointment).filter(
        models.Appointment.hospital_id == hospital.id
    ).count()
    
    # Get today's appointments
    today = date.today()
    todays_appointments = db.query(models.Appointment).filter(
        models.Appointment.hospital_id == hospital.id,
        func.date(models.Appointment.start_time) == today
    ).count()
    
    return {
        "hospital_id": str(hospital.id),
        "hospital_name": hospital.name,
        "total_doctors": total_doctors,
        "total_staff": total_staff,
        "total_appointments": total_appointments,
        "todays_appointments": todays_appointments,
        "is_verified": hospital.is_verified
    }


@router.get("/doctors")
def get_doctors(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all doctors linked to this organization.
    """
    if current_user.role != "organization":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Get organization's hospital
    hospital = db.query(models.Hospital).first()
    
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    doctors = db.query(models.Doctor).filter(
        models.Doctor.hospital_id == hospital.id
    ).all()
    
    result = []
    for doctor in doctors:
        user = db.query(models.User).filter(models.User.id == doctor.user_id).first()
        
        result.append({
            "id": str(doctor.id),
            "name": user.full_name if user else "Unknown",
            "email": user.email if user else "Unknown",
            "specialization": doctor.specialization,
            "is_verified": doctor.is_verified,
            "avg_rating": doctor.avg_rating,
            "total_reviews": doctor.total_reviews
        })
    
    return result


@router.get("/staff")
def get_staff(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all staff members of this organization.
    """
    if current_user.role != "organization":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Get organization's hospital
    hospital = db.query(models.Hospital).first()
    
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    staff_members = db.query(models.Staff).filter(
        models.Staff.hospital_id == hospital.id
    ).all()
    
    result = []
    for staff in staff_members:
        user = db.query(models.User).filter(models.User.id == staff.user_id).first()
        
        result.append({
            "id": str(staff.id),
            "name": user.full_name if user else "Unknown",
            "email": user.email if user else "Unknown",
            "role": staff.role,
            "created_at": staff.created_at.isoformat()
        })
    
    return result


@router.post("/staff")
def add_staff(
    staff: schemas.StaffCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new staff member to the organization.
    """
    if current_user.role != "organization":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == staff.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify hospital exists
    hospital = db.query(models.Hospital).filter(
        models.Hospital.id == staff.hospital_id
    ).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Check if staff already exists
    existing_staff = db.query(models.Staff).filter(
        models.Staff.user_id == staff.user_id
    ).first()
    if existing_staff:
        raise HTTPException(status_code=400, detail="Staff member already exists")
    
    # Create new staff
    new_staff = models.Staff(
        user_id=staff.user_id,
        hospital_id=staff.hospital_id,
        role=staff.role,
        assigned_doctors=staff.assigned_doctors,
        assigned_shifts=staff.assigned_shifts
    )
    
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    
    return {
        "id": str(new_staff.id),
        "message": "Staff member added successfully"
    }


@router.get("/inventory")
def get_inventory(
    status: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get inventory items with optional status filter.
    """
    if current_user.role != "organization":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Get organization's hospital
    hospital = db.query(models.Hospital).first()
    
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    query = db.query(models.Inventory).filter(
        models.Inventory.hospital_id == hospital.id
    )
    
    if status:
        query = query.filter(models.Inventory.status == status)
    
    items = query.all()
    
    return [
        {
            "id": str(item.id),
            "item_name": item.item_name,
            "category": item.category,
            "quantity": item.quantity,
            "unit": item.unit,
            "status": item.status,
            "min_threshold": item.min_threshold,
            "cost_per_unit": item.cost_per_unit
        }
        for item in items
    ]


@router.post("/inventory")
def add_inventory_item(
    item: schemas.InventoryCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new inventory item.
    """
    if current_user.role != "organization":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Get organization's hospital
    hospital = db.query(models.Hospital).first()
    
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Determine status based on quantity and threshold
    status = "Good"
    if item.min_threshold:
        if item.quantity == 0:
            status = "Critical"
        elif item.quantity <= item.min_threshold:
            status = "Low"
    
    new_item = models.Inventory(
        hospital_id=hospital.id,
        item_name=item.item_name,
        category=item.category,
        quantity=item.quantity,
        unit=item.unit,
        min_threshold=item.min_threshold,
        max_threshold=item.max_threshold,
        reorder_quantity=item.reorder_quantity,
        cost_per_unit=item.cost_per_unit,
        status=status
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return {
        "id": str(new_item.id),
        "message": "Inventory item added successfully"
    }


@router.put("/inventory/{item_id}")
def update_inventory_item(
    item_id: str,
    quantity: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update inventory item quantity.
    """
    if current_user.role != "organization":
        raise HTTPException(status_code=403, detail="Access denied")
    
    item = db.query(models.Inventory).filter(
        models.Inventory.id == item_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Update quantity
    item.quantity = quantity
    
    # Update status based on new quantity
    if item.min_threshold:
        if quantity == 0:
            item.status = "Critical"
        elif quantity <= item.min_threshold:
            item.status = "Low"
        else:
            item.status = "Good"
    
    db.commit()
    
    return {
        "message": "Inventory item updated successfully",
        "new_quantity": quantity,
        "status": item.status
    }


@router.get("/finance")
def get_finance_reports(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get financial reports for the organization.
    """
    if current_user.role != "organization":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Get organization's hospital
    hospital = db.query(models.Hospital).first()
    
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    query = db.query(models.Revenue).filter(
        models.Revenue.hospital_id == hospital.id
    )
    
    # Apply date filters if provided
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(models.Revenue.created_at >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(models.Revenue.created_at <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    revenues = query.all()
    
    # Calculate totals
    total_revenue = sum(r.amount for r in revenues)
    total_insurance = sum(r.insurance_amount for r in revenues)
    total_patient = sum(r.patient_amount for r in revenues)
    
    return {
        "total_revenue": total_revenue,
        "total_insurance_amount": total_insurance,
        "total_patient_amount": total_patient,
        "transaction_count": len(revenues),
        "transactions": [
            {
                "id": str(r.id),
                "amount": r.amount,
                "service_type": r.service_type,
                "payment_status": r.payment_status,
                "payment_date": r.payment_date.isoformat() if r.payment_date else None,
                "created_at": r.created_at.isoformat()
            }
            for r in revenues
        ]
    }


@router.put("/profile")
def update_profile(
    profile: schemas.HospitalCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update organization profile.
    """
    if current_user.role != "organization":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Get organization's hospital
    hospital = db.query(models.Hospital).first()
    
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Update fields
    if profile.name:
        hospital.name = profile.name
    if profile.address:
        hospital.address = profile.address
    if profile.city:
        hospital.city = profile.city
    if profile.phone:
        hospital.phone = profile.phone
    if profile.email:
        hospital.email = profile.email
    
    db.commit()
    
    return {
        "message": "Profile updated successfully",
        "hospital_id": str(hospital.id)
    }
