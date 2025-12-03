import random
import string
from typing import Any, Dict, List

from database import AsyncSessionLocal
from services.user_service import UserService
from services.user_patient_access_service import UserPatientAccessService


def _user_to_dict(u: Any) -> Dict[str, Any]:
    return {
        "id": u.id,
        "username": u.username,
        "role": u.role,
        "patient_id": u.patient_id,
        "doctor_id": u.doctor_id,
        "carer_id": u.carer_id,
    }


async def handle_user_action(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    action = (action or "").lower()
    payload = payload or {}
    async with AsyncSessionLocal() as db:
        user_svc = UserService(db)
        upa_svc = UserPatientAccessService(db)

        if action == "create_user":
            username = payload.get("username")
            role = payload.get("role")
            if not username or not role:
                return {"status": "missing_fields", "missing": ["username", "role"], "message": "username and role are required"}
            password = payload.get("password") or "".join(random.choices(string.ascii_letters + string.digits, k=8))
            user = await user_svc.create(
                username=username,
                password=password,
                role=role,
                patient_id=payload.get("patient_id"),
                doctor_id=payload.get("doctor_id"),
                carer_id=payload.get("carer_id"),
            )
            # map access if patient_id provided
            if payload.get("patient_id"):
                await upa_svc.create(user_id=user.id, patient_id=payload["patient_id"])
            return {
                "status": "success",
                "action": action,
                "data": {**_user_to_dict(user), "password": password},
            }

        if action == "update_user":
            user_id = payload.get("user_id")
            if not user_id:
                return {"status": "missing_fields", "missing": ["user_id"], "message": "user_id is required"}
            data = {k: v for k, v in payload.items() if k not in {"user_id"}}
            user = await user_svc.update(user_id, **data)
            return {"status": "success", "action": action, "data": _user_to_dict(user)}

        if action == "delete_user":
            user_id = payload.get("user_id")
            if not user_id:
                return {"status": "missing_fields", "missing": ["user_id"], "message": "user_id is required"}
            await user_svc.delete(user_id)
            return {"status": "success", "action": action, "data": {"user_id": user_id}}

        if action == "list_users":
            users = await user_svc.list()
            return {"status": "success", "action": action, "data": [_user_to_dict(u) for u in users]}

        if action == "create_user_patient_access":
            if not (payload.get("user_id") and payload.get("patient_id")):
                return {"status": "missing_fields", "missing": ["user_id", "patient_id"], "message": "user_id and patient_id are required"}
            upa = await upa_svc.create(user_id=payload["user_id"], patient_id=payload["patient_id"])
            return {"status": "success", "action": action, "data": {"id": upa.id}}

        if action == "delete_user_patient_access":
            upa_id = payload.get("upa_id")
            if not upa_id:
                return {"status": "missing_fields", "missing": ["upa_id"], "message": "upa_id is required"}
            await upa_svc.delete(upa_id)
            return {"status": "success", "action": action, "data": {"id": upa_id}}

        if action == "list_user_patient_access":
            rows = await upa_svc.list()
            return {
                "status": "success",
                "action": action,
                "data": [{"id": r.id, "user_id": r.user_id, "patient_id": r.patient_id} for r in rows],
            }

        return {"status": "error", "message": f"Unsupported action: {action}"}
