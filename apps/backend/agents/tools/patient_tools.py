from typing import Any, Dict
from datetime import date

from database import AsyncSessionLocal
from services.patient_service import PatientService

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
        svc = PatientService(db)

        if action == "create_patient":
            missing = [f for f in REQUIRED_FIELDS if not payload.get(f)]
            if missing:
                return {"status": "missing_fields", "missing": missing, "message": "Please ask the user to provide the missing information."}
            p = await svc.create(**payload)
            return {"status": "success", "action": action, "data": {"patient_id": p.id, **_to_dict(p)}}

        if action == "read_patient":
            patient_id = payload.get("patient_id")
            if not patient_id:
                return {"status": "missing_fields", "missing": ["patient_id"], "message": "patient_id is required"}
            p = await svc.get(patient_id)
            return {"status": "success", "action": action, "data": _to_dict(p)}

        if action == "update_patient":
            patient_id = payload.get("patient_id")
            if not patient_id:
                return {"status": "missing_fields", "missing": ["patient_id"], "message": "patient_id is required"}
            data = {k: v for k, v in payload.items() if k != "patient_id"}
            if not data:
                return {"status": "missing_fields", "missing": REQUIRED_FIELDS, "message": "Provide fields to update"}
            p = await svc.update(patient_id, **data)
            return {"status": "success", "action": action, "data": _to_dict(p)}

        if action == "delete_patient":
            patient_id = payload.get("patient_id")
            if not patient_id:
                return {"status": "missing_fields", "missing": ["patient_id"], "message": "patient_id is required"}
            await svc.delete(patient_id)
            return {"status": "success", "action": action, "data": {"patient_id": patient_id}}

        if action == "list_patients":
            rows = await svc.list()
            return {"status": "success", "action": action, "data": [_to_dict(p) for p in rows]}

        return {"status": "error", "message": f"Unsupported action: {action}"}
