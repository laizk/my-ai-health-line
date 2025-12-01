from uuid import uuid4
from typing import Optional, List, Dict

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from google.genai import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.agent import runner, session_service, memory_service, APP_NAME, USER_ID
from agents.user_context import update_user_context_from_db
from database import get_db
from models.models import ConversationSession, ConversationMessage
from google.adk.sessions import InMemorySessionService

router = APIRouter()


class AskRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    user_name: Optional[str] = None


async def _ensure_db_session(db: AsyncSession, session_id: str, user_id: str):
    session_row = await db.scalar(
        select(ConversationSession).where(ConversationSession.session_id == session_id)
    )
    if session_row:
        return session_row

    session_row = ConversationSession(
        session_id=session_id,
        app_name=APP_NAME,
        user_id=user_id,
    )
    db.add(session_row)
    await db.commit()
    await db.refresh(session_row)
    return session_row


async def _get_latest_session_id(db: AsyncSession, user_id: str) -> Optional[str]:
    row = await db.scalar(
        select(ConversationSession.session_id)
        .where(ConversationSession.app_name == APP_NAME, ConversationSession.user_id == user_id)
        .order_by(ConversationSession.created_at.desc())
    )
    return row


async def _append_message(db: AsyncSession, session_id: str, role: str, content: str):
    msg = ConversationMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    await db.commit()


async def _load_history(db: AsyncSession, session_id: str) -> List[Dict[str, str]]:
    rows = (
        await db.scalars(
            select(ConversationMessage)
            .where(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.created_at)
        )
    ).all()
    return [{"role": r.role, "content": r.content, "timestamp": r.created_at.isoformat() if r.created_at else None} for r in rows]


async def _get_or_create_session(session_id: str, user_id: str):
    """Ensure a session exists in the session service."""
    try:
        return await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
    except Exception:
        return await session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )


@router.post("/ask")
async def ask_agent(req: AskRequest, db: AsyncSession = Depends(get_db)):
    user_id = (req.user_name or "").strip() or USER_ID
    await update_user_context_from_db(db, user_id)
    session_id = req.session_id
    if not session_id:
        session_id = await _get_latest_session_id(db, user_id) or str(uuid4())

    session = await _get_or_create_session(session_id=session_id, user_id=user_id)
    await memory_service.add_session_to_memory(session)

    print("✅ Session added to memory!")

    session_id = session.id  # ensure we use runner session id
    await _ensure_db_session(db, session_id, user_id=user_id)

    await _append_message(db, session_id, "user", req.prompt)

    query_content = types.Content(role="user", parts=[types.Part(text=req.prompt)])
    assistant_text = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=query_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            assistant_text = event.content.parts[0].text or ""

    if assistant_text:
        await _append_message(db, session_id, "assistant", assistant_text)

    history = await _load_history(db, session_id)

    return {
        "response": assistant_text,
        "session_id": session_id,
        "history": history,
    }


@router.get("/ask/history")
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    history = await _load_history(db, session_id)
    if not history:
        raise HTTPException(status_code=404, detail="No history for session_id")
    return {"session_id": session_id, "history": history}
