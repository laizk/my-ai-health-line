from typing import Any, Dict
from datetime import date

from database import AsyncSessionLocal
from services.condition_service import ConditionService

REQUIRED_FIELDS = ["patient_id", "condition_name", "severity_level", "diagnosed_date"]
ALLOWED_SEVERITIES = {"mild", "moderate", "severe"}


def _to_dict(c: Any) -> Dict[str, Any]:
    return {
        "id": c.id,
        "patient_id": c.patient_id,
        "condition_name": c.condition_name,
        "severity_level": c.severity_level,
        "diagnosed_date": str(c.diagnosed_date) if c.diagnosed_date else None,
    }


async def handle_condition_action(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    action = (action or "").lower()
    payload = payload or {}

    # normalize diagnosed_date
    if payload.get("diagnosed_date") and isinstance(payload["diagnosed_date"], str):
        try:
            payload["diagnosed_date"] = date.fromisoformat(payload["diagnosed_date"])
        except ValueError:
            return {"status": "error", "message": "diagnosed_date must be YYYY-MM-DD"}
    if not payload.get("diagnosed_date"):
        payload["diagnosed_date"] = date.today()

    # normalize severity_level
    if payload.get("severity_level"):
        sev = str(payload["severity_level"]).strip().lower()
        if sev in ALLOWED_SEVERITIES:
            payload["severity_level"] = sev
        else:
            return {
                "status": "missing_fields",
                "missing": ["severity_level"],
                "message": "severity_level must be one of: mild, moderate, severe. Please confirm.",
            }

    async with AsyncSessionLocal() as db:
        svc = ConditionService(db)

        if action == "create_condition":
            missing = [f for f in REQUIRED_FIELDS if not payload.get(f)]
            if missing:
                return {"status": "missing_fields", "missing": missing, "message": "Please provide missing fields."}
            c = await svc.create(**payload)
            return {"status": "success", "action": action, "data": _to_dict(c)}

        if action == "read_condition":
            cid = payload.get("condition_id")
            if not cid:
                return {"status": "missing_fields", "missing": ["condition_id"], "message": "condition_id is required"}
            c = await svc.get(cid)
            return {"status": "success", "action": action, "data": _to_dict(c)}

        if action == "update_condition":
            cid = payload.get("condition_id")
            if not cid:
                return {"status": "missing_fields", "missing": ["condition_id"], "message": "condition_id is required"}
            data = {k: v for k, v in payload.items() if k != "condition_id"}
            if not data:
                return {"status": "missing_fields", "missing": REQUIRED_FIELDS, "message": "Provide fields to update"}
            c = await svc.update(cid, **data)
            return {"status": "success", "action": action, "data": _to_dict(c)}

        if action == "delete_condition":
            cid = payload.get("condition_id")
            if not cid:
                return {"status": "missing_fields", "missing": ["condition_id"], "message": "condition_id is required"}
            await svc.delete(cid)
            return {"status": "success", "action": action, "data": {"condition_id": cid}}

        if action == "list_conditions":
            rows = await svc.list()
            return {"status": "success", "action": action, "data": [_to_dict(c) for c in rows]}

        return {"status": "error", "message": f"Unsupported action: {action}"}
