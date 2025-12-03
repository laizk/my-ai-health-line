from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.models import ConversationSessionConcierge, ConversationMessageConcierge

router = APIRouter(prefix="/ask", tags=["ask"])


@router.get("/history/by_user")
async def get_history_by_user(user_id: str, db: AsyncSession = Depends(get_db)):
    sessions = (
        await db.scalars(
            select(ConversationSessionConcierge.session_id)
            .where(ConversationSessionConcierge.user_id == user_id)
            .order_by(ConversationSessionConcierge.created_at.desc())
        )
    ).all()

    if not sessions:
        raise HTTPException(status_code=404, detail="No history for user")

    history = (
        await db.scalars(
            select(ConversationMessageConcierge)
            .where(ConversationMessageConcierge.session_id.in_(sessions))
            .order_by(ConversationMessageConcierge.created_at)
        )
    ).all()

    return {
        "user_id": user_id,
        "sessions": sessions,
        "history": [
            {
                "session_id": msg.session_id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in history
        ],
    }
