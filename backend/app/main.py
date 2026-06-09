import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import init_db
# AICI ESTE SECRETUL: Importăm modelele ca SQLAlchemy să afle de existența lor!
from app.models import user, journey

from app.api.routers import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Acum când init_db() rulează, știe că trebuie să creeze tabelele din fișierele de mai sus
    init_db()
    
    # Seed the Demo Student User for the Autonomous Student Demo
    from app.db.database import SessionLocal
    from app.crud.crud_user import get_user_by_email, create_user
    from app.schemas.user import UserCreate
    
    with SessionLocal() as db:
        demo_email = "demo_student@aicoach.com"
        if not get_user_by_email(db, email=demo_email):
            print("Seeding Demo Student user...")
            create_user(db, user=UserCreate(email=demo_email, password="demopassword123"))
    
    yield

app = FastAPI(title="AI Coding Coaching Platform", lifespan=lifespan)


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Add production origins from environment if present
env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
    origins.extend(env_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "API & Hybrid AI Setup is running"}
