from datetime import date
from typing import Any, Dict

from database import AsyncSessionLocal
from services.carer_service import CarerService

REQUIRED_FIELDS = [
    "patient_id",
    "full_name",
    "relationship_to_patient",
    "contact_number",
]


def _to_dict(c: Any) -> Dict[str, Any]:
    return {
        "id": c.id,
        "patient_id": c.patient_id,
        "full_name": c.full_name,
        "relationship_to_patient": c.relationship_to_patient,
        "contact_number": c.contact_number,
        "notes": c.notes,
    }


async def handle_carer_action(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Async dispatcher for carer CRUD actions (FunctionTool-friendly)."""
    action = (action or "").lower()
    payload = payload or {}

    async with AsyncSessionLocal() as db:
        svc = CarerService(db)

        if action == "create_carer":
            missing = [f for f in REQUIRED_FIELDS if payload.get(f) in (None, "", [])]
            if missing:
                return {
                    "status": "missing_fields",
                    "missing": missing,
                    "message": "Please ask the user to provide the missing information.",
                }
            carer = await svc.create(**payload)
            return {"status": "success", "action": action, "data": _to_dict(carer)}

        if action == "read_carer":
            carer_id = payload.get("carer_id")
            if not carer_id:
                return {"status": "missing_fields", "missing": ["carer_id"], "message": "carer_id is required"}
            carer = await svc.get(carer_id)
            return {"status": "success", "action": action, "data": _to_dict(carer)}

        if action == "update_carer":
            carer_id = payload.get("carer_id")
            if not carer_id:
                return {"status": "missing_fields", "missing": ["carer_id"], "message": "carer_id is required"}
            data = {k: v for k, v in payload.items() if k != "carer_id"}
            if not data:
                return {"status": "missing_fields", "missing": REQUIRED_FIELDS, "message": "Provide fields to update"}
            carer = await svc.update(carer_id, **data)
            return {"status": "success", "action": action, "data": _to_dict(carer)}

        if action == "delete_carer":
            carer_id = payload.get("carer_id")
            if not carer_id:
                return {"status": "missing_fields", "missing": ["carer_id"], "message": "carer_id is required"}
            await svc.delete(carer_id)
            return {"status": "success", "action": action, "data": {"carer_id": carer_id}}

        if action == "list_carers":
            rows = await svc.list()
            return {"status": "success", "action": action, "data": [_to_dict(c) for c in rows]}

        return {"status": "error", "message": f"Unsupported action: {action}"}
