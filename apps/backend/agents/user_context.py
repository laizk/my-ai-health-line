from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import UserAccount, Patient, Doctor, Carer
from agents.tools import set_current_user


async def update_user_context_from_db(db: AsyncSession, username: Optional[str]) -> None:
    """
    Populate the in-memory user context from the database using the username.

    Falls back to guest if the user is not found.
    """
    if not username:
        set_current_user("guest_user", full_name="Guest", role="guest")
        return

    user = await db.scalar(select(UserAccount).where(UserAccount.username == username))
    if not user:
        set_current_user("guest_user", full_name="Guest", role="guest")
        return

    role = (user.role or "guest").lower()
    display_name = user.username

    # Try to resolve a nicer display name for patient/doctor roles
    if role == "patient" and user.patient_id:
        patient = await db.scalar(select(Patient).where(Patient.id == user.patient_id))
        if patient:
            display_name = patient.full_name
    elif role == "doctor" and user.doctor_id:
        doctor = await db.scalar(select(Doctor).where(Doctor.id == user.doctor_id))
        if doctor:
            display_name = doctor.full_name
    elif role == "carer" and user.carer_id:
        carer = await db.scalar(select(Carer).where(Carer.id == user.carer_id))
        if carer:
            display_name = carer.full_name

    set_current_user(user.username, full_name=display_name, role=role)
