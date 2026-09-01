"""
SatyaKavach - Database Configuration
Async SQLAlchemy setup with PostgreSQL
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def _async_db_url(url: str) -> str:
    """Normalize a DATABASE_URL for SQLAlchemy + asyncpg.

    - Accepts plain 'postgresql://' / 'postgres://' (as given by Neon) and
      rewrites to 'postgresql+asyncpg://' so the async driver is used.
    - Strips 'sslmode=...' from the query string (asyncpg doesn't accept it)
      and re-adds it as 'ssl=require' so encrypted connections still work.
    """
    from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

    url = url.strip()
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
            "postgres://", "postgresql+asyncpg://", 1
        )
    if not url.startswith("postgresql+asyncpg://"):
        return url

    parts = urlsplit(url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    sslmode = next((v for k, v in query if k.lower() == "sslmode"), None)
    query = [(k, v) for k, v in query if k.lower() != "sslmode"]
    if sslmode in ("require", "verify-ca", "verify-full", "prefer"):
        query.append(("ssl", "require"))
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
    )


engine = create_async_engine(
    _async_db_url(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    class_=AsyncSession,
    bind=engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency: yield an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables (dev convenience — use Alembic in production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Dispose engine on shutdown."""
    await engine.dispose()
