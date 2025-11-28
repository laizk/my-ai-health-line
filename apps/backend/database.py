from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,               # set True for debugging queries
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_db():
    """FastAPI dependency: yields an async session."""
    async with AsyncSessionLocal() as session:
        yield session
