from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth import login as auth_login

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/login")
async def login(credentials: dict, db: AsyncSession = Depends(get_db)):
    """Alias to the unified auth login endpoint (supports patient/carer/doctor/admin)."""
    return await auth_login(credentials, db)
