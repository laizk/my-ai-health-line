from datetime import date, time
from typing import Any, Dict

from database import AsyncSessionLocal
from services.medication_schedule_service import MedicationScheduleService

ALLOWED_STATUS = {"taken", "pending", "missed"}

REQUIRED_FIELDS = [
    "patient_id",
    "medication_name",
    "dosage",
    "frequency",
    "intake_time",
    "start_date",
    "end_date",
    "status",
]


def _to_dict(m: Any) -> Dict[str, Any]:
    return {
        "id": m.id,
        "patient_id": m.patient_id,
        "medication_name": m.medication_name,
        "dosage": m.dosage,
        "frequency": m.frequency,
        "intake_time": m.intake_time.isoformat() if m.intake_time else None,
        "start_date": str(m.start_date) if m.start_date else None,
        "end_date": str(m.end_date) if m.end_date else None,
        "status": m.status,
        "remarks": m.remarks,
    }


def _normalize_dates(payload: Dict[str, Any]) -> Dict[str, Any]:
    for fld in ("start_date", "end_date"):
        if payload.get(fld) and isinstance(payload[fld], str):
            try:
                payload[fld] = date.fromisoformat(payload[fld])
            except ValueError:
                raise ValueError(f"{fld} must be YYYY-MM-DD")
    return payload


def _normalize_intake_time(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw = payload.get("intake_time")
    if raw is None:
        return payload

    if isinstance(raw, time):
        return payload

    if isinstance(raw, str):
        txt = raw.strip()
        try:
            parsed = time.fromisoformat(txt)
            payload["intake_time"] = parsed
            return payload
        except ValueError:
            if len(txt) == 5:  # allow HH:MM by appending seconds
                try:
                    parsed = time.fromisoformat(f"{txt}:00")
                    payload["intake_time"] = parsed
                    return payload
                except ValueError:
                    pass
            raise ValueError("intake_time must be a valid 24-hour time (HH:MM or HH:MM:SS)")
    raise ValueError("intake_time must be a valid 24-hour time (HH:MM or HH:MM:SS)")


def _validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing = [f for f in REQUIRED_FIELDS if not payload.get(f)]
    if missing:
        return {"status": "missing_fields", "missing": missing, "message": "Please provide missing fields."}

    # normalize status
    status = str(payload.get("status", "")).lower()
    if status not in ALLOWED_STATUS:
        return {"status": "missing_fields", "missing": ["status"], "message": "status must be one of: taken, pending, missed"}
    payload["status"] = status

    # normalize medication_name
    med = str(payload.get("medication_name", "")).strip().lower()
    payload["medication_name"] = med

    # dates
    try:
        payload = _normalize_dates(payload)
        payload = _normalize_intake_time(payload)
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    return None  # no issues


async def handle_medication_action(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    action = (action or "").lower()
    payload = payload or {}

    async with AsyncSessionLocal() as db:
        svc = MedicationScheduleService(db)

        if action == "create_medication":
            validation = _validate_payload(payload)
            if validation:
                return validation
            m = await svc.create(**payload)
            return {"status": "success", "action": action, "data": _to_dict(m)}

        if action == "read_medication":
            mid = payload.get("medication_id")
            if not mid:
                return {"status": "missing_fields", "missing": ["medication_id"], "message": "medication_id is required"}
            m = await svc.get(mid)
            return {"status": "success", "action": action, "data": _to_dict(m)}

        if action == "update_medication":
            mid = payload.get("medication_id")
            if not mid:
                return {"status": "missing_fields", "missing": ["medication_id"], "message": "medication_id is required"}
            data = {k: v for k, v in payload.items() if k != "medication_id"}
            if not data:
                return {"status": "missing_fields", "missing": REQUIRED_FIELDS, "message": "Provide fields to update"}
            # validate fields if provided
            if data.get("status") or data.get("medication_name") or data.get("start_date") or data.get("end_date") or data.get("intake_time"):
                validation = _validate_payload({**payload, **data})
                if validation:
                    return validation
                data = {k: v for k, v in payload.items() if k != "medication_id"}
            try:
                data = _normalize_dates(data)
                if "intake_time" in data:
                    data = _normalize_intake_time(data)
            except ValueError as e:
                return {"status": "error", "message": str(e)}
            m = await svc.update(mid, **data)
            return {"status": "success", "action": action, "data": _to_dict(m)}

        if action == "delete_medication":
            mid = payload.get("medication_id")
            if not mid:
                return {"status": "missing_fields", "missing": ["medication_id"], "message": "medication_id is required"}
            await svc.delete(mid)
            return {"status": "success", "action": action, "data": {"medication_id": mid}}

        if action == "list_medications":
            rows = await svc.list()
            return {"status": "success", "action": action, "data": [_to_dict(m) for m in rows]}

        return {"status": "error", "message": f"Unsupported action: {action}"}
