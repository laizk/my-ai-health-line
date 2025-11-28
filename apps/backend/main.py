from fastapi import FastAPI

from agents.routes import router as agent_router
from routes.patients import router as patient_router
from config import settings
from database import DATABASE_URL

app = FastAPI(title="My AI Health Line Backend")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/debug/env")
def debug_env():
    return {
        "DB_HOST": settings.DB_HOST,
        "DB_USER": settings.DB_USER,
        "url": DATABASE_URL
    }

# 👉 Register routes
app.include_router(agent_router)          # /ask
app.include_router(patient_router)        # /patients/*
