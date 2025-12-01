from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.models import UserAccount, Patient, UserPatientAccess, Doctor

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(credentials: dict, db: AsyncSession = Depends(get_db)):
    username = credentials.get("username")
    password = credentials.get("password")

    user = await db.scalar(
        select(UserAccount).where(
            UserAccount.username == username,
            UserAccount.password == password,
        )
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    role = (user.role or "").lower()
    patients_payload = []

    display_name = user.username

    if role == "patient":
        patient = await db.scalar(select(Patient).where(Patient.id == user.patient_id))
        if patient:
            display_name = patient.full_name

    if role == "doctor":
        doctor = await db.scalar(select(Doctor).where(Doctor.id == user.doctor_id))
        if doctor:
            display_name = doctor.full_name

    if role in {"patient", "carer"}:
        access_rows = (
            await db.scalars(
                select(UserPatientAccess.patient_id).where(UserPatientAccess.user_id == user.id)
            )
        ).all()
        patient_ids = list(set(access_rows))
        if not patient_ids and role == "patient" and user.patient_id:
            patient_ids = [user.patient_id]
        if not patient_ids:
            raise HTTPException(status_code=400, detail="No patient access configured")
        patient_rows = (
            await db.scalars(select(Patient).where(Patient.id.in_(patient_ids)))
        ).all()
        patients_payload = [{"id": p.id, "full_name": p.full_name} for p in patient_rows]

    elif role in {"doctor", "admin"}:
        patient_rows = (await db.scalars(select(Patient))).all()
        patients_payload = [{"id": p.id, "full_name": p.full_name} for p in patient_rows]

    else:
        raise HTTPException(status_code=400, detail="Unsupported role")

    return {
        "role": role,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": display_name,
        },
        "patients": patients_payload,
    }
