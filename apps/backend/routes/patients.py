from datetime import date

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from database import get_db
from models.models import Patient, Condition, Appointment, Referral, Doctor, Carer, MedicationSchedule
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

    # Medication schedules
    meds = (
        await db.scalars(
            select(MedicationSchedule).where(MedicationSchedule.patient_id == patient_id)
        )
    ).all()
    meds_payload = [
        {
            "id": m.id,
            "medication_name": m.medication_name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "start_date": m.start_date,
            "end_date": m.end_date,
            "intake_time": m.intake_time.isoformat() if m.intake_time else None,
            "status": m.status,
            "remarks": m.remarks,
        }
        for m in meds
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
        "medications": meds_payload,
    }
