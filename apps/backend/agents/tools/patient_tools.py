from typing import Any, Dict
from datetime import date
import random
import string

from database import AsyncSessionLocal
from services.patient_service import PatientService
from services.user_service import UserService
from services.user_patient_access_service import UserPatientAccessService

REQUIRED_FIELDS = [
    "full_name",
    "birthdate",
    "gender",
    "contact_number",
    "address",
    "emergency_contact",
]


def _to_dict(p: Any) -> Dict[str, Any]:
    return {
        "id": p.id,
        "full_name": p.full_name,
        "birthdate": str(p.birthdate) if p.birthdate else None,
        "gender": p.gender,
        "contact_number": p.contact_number,
        "address": p.address,
        "emergency_contact": p.emergency_contact,
    }


async def handle_patient_action(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Async dispatcher for patient CRUD actions (to be used as an async FunctionTool)."""
    action = (action or "").lower()
    payload = payload or {}

    # normalize birthdate if provided as string
    if payload.get("birthdate") and isinstance(payload["birthdate"], str):
        try:
            payload["birthdate"] = date.fromisoformat(payload["birthdate"])
        except ValueError:
            return {"status": "error", "message": "birthdate must be YYYY-MM-DD"}

    async with AsyncSessionLocal() as db:
        patient_svc = PatientService(db)
        user_svc = UserService(db)
        upa_svc = UserPatientAccessService(db)

        if action == "create_patient":
            missing = [f for f in REQUIRED_FIELDS if not payload.get(f)]
            if missing:
                return {"status": "missing_fields", "missing": missing, "message": "Please ask the user to provide the missing information."}
            p = await patient_svc.create(**payload)

            # auto-create user and access mapping
            base_name = (payload.get("full_name") or "").strip().lower().replace(" ", ".")
            username = payload.get("username") or (base_name if base_name else f"patient_{p.id}")
            password = "".join(random.choices(string.ascii_letters + string.digits, k=8))
            user = await user_svc.create(
                username=username,
                password=password,
                role="patient",
                patient_id=p.id,
                doctor_id=None,
                carer_id=None,
            )
            await upa_svc.create(user_id=user.id, patient_id=p.id)

            return {
                "status": "success",
                "action": action,
                "data": {
                    "patient_id": p.id,
                    **_to_dict(p),
                    "user": {"id": user.id, "username": user.username, "role": user.role},
                },
            }

        if action == "read_patient":
            patient_id = payload.get("patient_id")
            full_name = payload.get("full_name")
            bdate = payload.get("birthdate")
            if patient_id:
                p = await patient_svc.get(patient_id)
                return {"status": "success", "action": action, "data": _to_dict(p)}
            if full_name and bdate:
                rows = await patient_svc.list()
                for p in rows:
                    if p.full_name == full_name and p.birthdate == bdate:
                        return {"status": "success", "action": action, "data": _to_dict(p)}
                return {"status": "error", "message": "Patient not found with provided full_name and birthdate"}
            return {
                "status": "missing_fields",
                "missing": ["patient_id or full_name+birthdate"],
                "message": "Provide patient_id or full_name + birthdate (YYYY-MM-DD)",
            }

        if action == "update_patient":
            patient_id = payload.get("patient_id")
            if not patient_id:
                return {"status": "missing_fields", "missing": ["patient_id"], "message": "patient_id is required"}
            data = {k: v for k, v in payload.items() if k != "patient_id"}
            if not data:
                return {"status": "missing_fields", "missing": REQUIRED_FIELDS, "message": "Provide fields to update"}
            p = await patient_svc.update(patient_id, **data)
            return {"status": "success", "action": action, "data": _to_dict(p)}

        if action == "delete_patient":
            patient_id = payload.get("patient_id")
            if not patient_id:
                return {"status": "missing_fields", "missing": ["patient_id"], "message": "patient_id is required"}
            await patient_svc.delete(patient_id)
            return {"status": "success", "action": action, "data": {"patient_id": patient_id}}

        if action == "list_patients":
            rows = await patient_svc.list()
            return {"status": "success", "action": action, "data": [_to_dict(p) for p in rows]}

        return {"status": "error", "message": f"Unsupported action: {action}"}
