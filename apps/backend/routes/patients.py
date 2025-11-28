from datetime import date

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from database import get_db
from models.models import Patient, Condition, Appointment, Referral, Doctor, Carer
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/patients", tags=["patients"])


def _calculate_age_group(birthdate: date | None):
    """Return (age, group) where group can be minor/elderly/adult/None."""
    if not birthdate:
        return None, None

    today = date.today()
    age = (
        today.year
        - birthdate.year
        - ((today.month, today.day) < (birthdate.month, birthdate.day))
    )
    if age < 18:
        return age, "minor"
    if age >= 65:
        return age, "elderly"
    return age, "adult"


class LoginRequest(BaseModel):
    role: str
    username: str
    password: str


@router.post("/login")
async def login_user(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    role = credentials.role.lower()

    if role not in {"patient", "carer"}:
        raise HTTPException(status_code=400, detail="role must be 'patient' or 'carer'")

    if role == "patient":
        patient = await db.scalar(
            select(Patient).where(
                Patient.login_username == credentials.username,
                Patient.login_password == credentials.password,
            )
        )
        if not patient:
            raise HTTPException(status_code=401, detail="Invalid patient credentials")

        return {
            "role": "patient",
            "user": {"id": patient.id, "full_name": patient.full_name},
            "patients": [{"id": patient.id, "full_name": patient.full_name}],
        }

    # Carer
    carers = (
        await db.scalars(
            select(Carer).where(
                Carer.login_username == credentials.username,
                Carer.login_password == credentials.password,
            )
        )
    ).all()

    if not carers:
        raise HTTPException(status_code=401, detail="Invalid carer credentials")

    patient_ids = {c.patient_id for c in carers if c.patient_id}
    patient_rows = (
        await db.scalars(
            select(Patient).where(Patient.id.in_(patient_ids))
        )
    ).all() if patient_ids else []

    patients_payload = [
        {"id": p.id, "full_name": p.full_name}
        for p in patient_rows
    ]

    return {
        "role": "carer",
        "user": {
            "id": carers[0].id,
            "full_name": carers[0].full_name,
        },
        "patients": patients_payload,
    }


@router.get("/{patient_id}")
async def get_patient_profile(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):

    # Patient
    patient = await db.scalar(
        select(Patient).where(Patient.id == patient_id)
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    age, age_group = _calculate_age_group(patient.birthdate)
    patient_payload = {
        "id": patient.id,
        "full_name": patient.full_name,
        "birthdate": patient.birthdate,
        "gender": patient.gender,
        "contact_number": patient.contact_number,
        "address": patient.address,
        "emergency_contact": patient.emergency_contact,
        "age": age,
        "age_group": age_group,
        "requires_carer": age_group in {"minor", "elderly"},
    }

    # Conditions
    conditions = (
        await db.scalars(
            select(Condition).where(Condition.patient_id == patient_id)
        )
    ).all()

    # Carers / guardians
    carers = (
        await db.scalars(
            select(Carer).where(Carer.patient_id == patient_id)
        )
    ).all()
    carers_payload = [
        {
            "id": c.id,
            "full_name": c.full_name,
            "relationship_to_patient": c.relationship_to_patient,
            "contact_number": c.contact_number,
            "notes": c.notes,
        }
        for c in carers
    ]

    # Appointments (with doctor join)
    appts_raw = (
        await db.execute(
            select(Appointment, Doctor)
            .join(Doctor, Appointment.doctor_id == Doctor.id, isouter=True)
            .where(Appointment.patient_id == patient_id)
        )
    ).all()

    appointments = [
        {
            "appointment_id": a.Appointment.id,
            "doctor": a.Doctor.full_name if a.Doctor else None,
            "specialization": a.Doctor.specialization if a.Doctor else None,
            "date": a.Appointment.appointment_date,
            "status": a.Appointment.status,
        }
        for a in appts_raw
    ]

    # Referrals
    referrals = (
        await db.scalars(
            select(Referral)
            .join(Appointment, Referral.appointment_id == Appointment.id)
            .where(Appointment.patient_id == patient_id)
        )
    ).all()

    return {
        "patient": patient_payload,
        "conditions": conditions,
        "appointments": appointments,
        "referrals": referrals,
        "carers": carers_payload,
    }
