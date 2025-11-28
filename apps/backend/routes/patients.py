from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from database import get_db
from models.models import Patient, Condition, Appointment, Referral, Doctor
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/patients", tags=["patients"])

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

    # Conditions
    conditions = (
        await db.scalars(
            select(Condition).where(Condition.patient_id == patient_id)
        )
    ).all()

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
        "patient": patient,
        "conditions": conditions,
        "appointments": appointments,
        "referrals": referrals,
    }
