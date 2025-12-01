from typing import Any, Dict, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDService:
    """Base CRUD helper; subclasses must set `model`."""

    model: Type[Any]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self):
        return (await self.db.scalars(select(self.model))).all()

    async def get(self, obj_id: int):
        obj = await self.db.scalar(select(self.model).where(self.model.id == obj_id))
        if not obj:
            raise ValueError(f"{self.model.__name__} not found")
        return obj

    async def create(self, **data):
        obj = self.model(**data)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj_id: int, **data):
        obj = await self.get(obj_id)
        for k, v in data.items():
            setattr(obj, k, v)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj_id: int):
        obj = await self.get(obj_id)
        await self.db.delete(obj)
        await self.db.commit()
        return {"status": "deleted", "id": obj_id}
