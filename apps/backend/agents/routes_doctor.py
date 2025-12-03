from uuid import uuid4
from typing import Optional, List, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.doctor_assistant_agent import runner as doctor_runner, session_service, memory_service, APP_NAME as DOCTOR_APP
from agents.user_context import update_user_context_from_db
from database import get_db
from models.models import ConversationSessionDoctor, ConversationMessageDoctor
from google.genai import types

router = APIRouter(prefix="/doctor", tags=["doctor_ai"])


class DoctorAskRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    user_name: Optional[str] = None


async def _ensure_db_session(db: AsyncSession, session_id: str, user_id: str):
    row = await db.scalar(
        select(ConversationSessionDoctor).where(ConversationSessionDoctor.session_id == session_id)
    )
    if row:
        return row
    row = ConversationSessionDoctor(session_id=session_id, app_name=DOCTOR_APP, user_id=user_id)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def _append_message(db: AsyncSession, session_id: str, role: str, content: str):
    msg = ConversationMessageDoctor(session_id=session_id, role=role, content=content)
    db.add(msg)
    await db.commit()


async def _load_history(db: AsyncSession, session_id: str) -> List[Dict[str, str]]:
    rows = (
        await db.scalars(
            select(ConversationMessageDoctor)
            .where(ConversationMessageDoctor.session_id == session_id)
            .order_by(ConversationMessageDoctor.created_at)
        )
    ).all()
    return [
        {"role": r.role, "content": r.content, "timestamp": r.created_at.isoformat() if r.created_at else None}
        for r in rows
    ]


@router.post("/ask")
async def ask_doctor_agent(req: DoctorAskRequest, db: AsyncSession = Depends(get_db)):
    user_id = (req.user_name or "").strip() or "doctor_user"
    session_id = req.session_id or str(uuid4())

    # hydrate user context (username/role) for identify_user tool
    await update_user_context_from_db(db, user_id)

    # ensure session in google adk
    try:
        sess = await session_service.create_session(app_name=DOCTOR_APP, user_id=user_id, session_id=session_id)
    except Exception:
        sess = await session_service.get_session(app_name=DOCTOR_APP, user_id=user_id, session_id=session_id)

    await memory_service.add_session_to_memory(sess)
    await _ensure_db_session(db, session_id, user_id=user_id)
    await _append_message(db, session_id, "user", req.prompt)

    query_content = types.Content(role="user", parts=[types.Part(text=req.prompt)])
    assistant_text = ""

    async for event in doctor_runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=query_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            assistant_text = event.content.parts[0].text or ""

    if assistant_text:
        await _append_message(db, session_id, "assistant", assistant_text)

    history = await _load_history(db, session_id)
    return {"response": assistant_text, "session_id": session_id, "history": history}


@router.get("/ask/history")
async def doctor_history(session_id: str, db: AsyncSession = Depends(get_db)):
    history = await _load_history(db, session_id)
    if not history:
        raise HTTPException(status_code=404, detail="No history for session_id")
    return {"session_id": session_id, "history": history}
