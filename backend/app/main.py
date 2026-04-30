from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.api.routers import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="AI Coding Coaching Platform", lifespan=lifespan)

origins = [
    "http://localhost:5173",    # Portul tău de React/Vite
    "http://127.0.0.1:5173",  # Uneori Windows preferă IP-ul în loc de localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Permitem aceste adrese
    allow_credentials=True,
    allow_methods=["*"],              # Permitem toate metodele (GET, POST, etc.)
    allow_headers=["*"],              # Permitem toate headerele
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "API & Hybrid AI Setup is running"}
