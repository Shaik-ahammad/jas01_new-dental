# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from passlib.context import CryptContext
from datetime import datetime, timedelta, date
from jose import jwt, JWTError
from typing import List

# Import your local modules
import models
import database
import schemas
from agents.router import AgentRouter

# --- CONFIGURATION & CONSTANTS ---
SECRET_KEY = "alshifa_super_secret_key_change_this_in_prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 Hours

# --- SECURITY SETUP ---
# bcrypt is strictly configured to avoid version conflicts
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- DATABASE SETUP ---
models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- AGENT INITIALIZATION ---
ai_router_service = AgentRouter()

# ==============================================================================
# 1. AUTHENTICATION & UTILS (CRITICAL FIX APPLIED)
# ==============================================================================

def get_password_hash(password):
    # FIX: The [:72] is MANDATORY for the bcrypt library in your environment.
    # Without this, registration will ALWAYS fail with Error 500.
    return pwd_context.hash(password[:72])

def verify_password(plain_password, hashed_password):
    # FIX: Truncate here too for consistency
    return pwd_context.verify(plain_password[:72], hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# ==============================================================================
# 2. ROUTERS
# ==============================================================================

# --- AUTH ROUTER ---
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Check Email
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Create User
    try:
        print(f"DEBUG: Registering {user.email}...") # Debug log
        
        # NOTE: We use the FIXED hashing function here
        hashed_pw = get_password_hash(user.password)
        
        new_user = models.User(
            email=user.email,
            password_hash=hashed_pw,
            full_name=user.full_name,
            role=user.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 3. Create Profile based on Role
        if user.role == "doctor":
            hospital = db.query(models.Hospital).first()
            if not hospital:
                hospital = models.Hospital(name="Al-Shifa Main Center", location="City Center")
                db.add(hospital)
                db.commit()
            
            new_profile = models.Doctor(
                user_id=new_user.id,
                hospital_id=hospital.id,
                specialization=user.specialization or "General Dentist",
                license_number=user.license_number
            )
            db.add(new_profile)

        elif user.role == "patient":
            new_profile = models.Patient(
                user_id=new_user.id,
                age=user.age,
                gender=user.gender
            )
            db.add(new_profile)

        db.commit()
        print("DEBUG: Registration Successful")
        return new_user
        
    except Exception as e:
        db.rollback()
        print(f"CRITICAL REGISTRATION ERROR: {str(e)}")
        # Return the specific error to the client for easier debugging
        raise HTTPException(status_code=500, detail=f"Registration Error: {str(e)}")

@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=403, detail="Invalid Credentials")

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}

@auth_router.get("/me")
def read_current_user(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile_data = {}
    if current_user.role == "doctor":
        profile = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.id).first()
        if profile: 
            profile_data = {
                "specialization": profile.specialization, 
                "hospital_id": str(profile.hospital_id),
                "schedule_config": {
                    "slot_duration": profile.slot_duration,
                    "break_duration": profile.break_duration,
                    "work_start": profile.work_start_time,
                    "work_end": profile.work_end_time
                }
            }
    elif current_user.role == "patient":
        profile = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
        if profile: profile_data = {"age": profile.age, "gender": profile.gender}
        
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "details": profile_data
    }

# --- DOCTOR ROUTER ---
doctor_router = APIRouter(prefix="/doctor", tags=["Doctor Dashboard"])

@doctor_router.get("/dashboard")
def get_dashboard_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "doctor": raise HTTPException(403, "Access Denied")
    doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.id).first()
    
    today = date.today()
    todays_appts = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor.id, 
        func.date(models.Appointment.start_time) == today
    ).all()
    
    return {
        "today_count": len(todays_appts),
        "revenue": len(todays_appts) * 1500,
        "active_patients": 124, 
        "appointments": [{"id": str(a.id), "time": a.start_time.strftime("%H:%M"), "status": a.status} for a in todays_appts]
    }

@doctor_router.put("/config")
def update_schedule_config(config: schemas.DoctorScheduleConfig, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "doctor": raise HTTPException(403, "Only doctors can configure schedules")
    doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.id).first()
    if not doctor: raise HTTPException(404, "Doctor profile not found")
    
    doctor.slot_duration = config.slot_duration
    doctor.break_duration = config.break_duration
    doctor.work_start_time = config.work_start
    doctor.work_end_time = config.work_end
    db.commit()
    return {"status": "success", "message": "AI Scheduler updated successfully"}

# --- AI AGENT ROUTER ---
agent_api_router = APIRouter(prefix="/agent", tags=["AI Agents"])

@agent_api_router.post("/execute")
async def execute_agent_logic(request: Request):
    payload = await request.json()
    if "user_query" not in payload: raise HTTPException(400, "user_query is required")
    try:
        return await ai_router_service.route(payload)
    except Exception as e:
        print(f"Agent Error: {e}")
        return {"response_text": "I'm having trouble connecting to the neural network.", "action_taken": "error"}

@agent_api_router.get("/memory/inventory")
def read_inventory_memory(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "doctor": raise HTTPException(403, "Access Denied")
    inventory_data = ai_router_service.agents["inventory"].memory.graph 
    return [{"id": k, "name": v["name"], "stock": v["stock"]} for k, v in inventory_data.items()]

app = FastAPI(title="Al-Shifa API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(doctor_router)
app.include_router(agent_api_router)

@app.get("/")
def health_check():
    return {"status": "operational", "system": "Al-Shifa Neural Core", "time": datetime.now()}