# backend/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import get_db
import models
import database
from config import CORS_ORIGINS
from routers import auth, doctor, patient, admin, organization
from agents.router import AgentRouter

# --- DATABASE SETUP ---
models.Base.metadata.create_all(bind=database.engine)

# --- AGENT INITIALIZATION ---
ai_router_service = AgentRouter()

# --- FASTAPI APP ---
app = FastAPI(
    title="Al-Shifa Dental Intelligence System",
    version="2.0.0",
    description="Comprehensive dental practice management system with AI capabilities"
)

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUDE ROUTERS ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(doctor.router, prefix="/doctor", tags=["Doctor"])
app.include_router(patient.router, prefix="/patient", tags=["Patient"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(organization.router, prefix="/organization", tags=["Organization"])

# --- AI AGENT ENDPOINTS (Legacy) ---
@app.post("/agent/execute", tags=["AI Agents"])
async def execute_agent_logic(request: Request):
    """Execute AI agent logic."""
    payload = await request.json()
    if "user_query" not in payload:
        return {"error": "user_query is required"}
    try:
        return await ai_router_service.route(payload)
    except Exception as e:
        print(f"Agent Error: {e}")
        return {
            "response_text": "I'm having trouble connecting to the neural network.",
            "action_taken": "error"
        }

@app.get("/agent/memory/inventory", tags=["AI Agents"])
def read_inventory_memory():
    """Read inventory memory from AI agent."""
    try:
        inventory_data = ai_router_service.agents["inventory"].memory.graph
        return [
            {"id": k, "name": v["name"], "stock": v["stock"]}
            for k, v in inventory_data.items()
        ]
    except Exception as e:
        return {"error": str(e)}

# --- HEALTH CHECK ENDPOINTS ---
@app.get("/", tags=["Health"])
def root():
    """Root endpoint."""
    return {
        "message": "Al-Shifa Dental API v2.0 - Running",
        "status": "operational",
        "system": "Al-Shifa Neural Core"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
