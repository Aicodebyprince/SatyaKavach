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
    - asyncpg only understands a small set of URL query params. Provider URLs
      (Neon/Render) append params like 'sslmode', 'channel_binding',
      'target_session_attrs' that asyncpg rejects — those are stripped.
    - If the provider requested SSL ('sslmode=require' etc.), it is re-added
      as 'ssl=require' which asyncpg accepts.
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
    wants_ssl = sslmode in ("require", "verify-ca", "verify-full", "prefer")

    # asyncpg-supported query params (everything else is stripped)
    supported = {
        "user", "password", "host", "port", "database",
        "ssl", "sslrootcert", "sslkey", "sslcert",
        "connect_timeout", "statement_cache_size", "max_cached_statement_lifetime",
        "max_cacheable_statement_size", "command_timeout", "server_settings",
        "tcp_user_timeout", "application_name",
    }
    cleaned = [(k, v) for k, v in query if k.lower() in supported]

    # Ensure SSL is requested when the provider URL asked for it
    has_ssl = any(k.lower() == "ssl" for k, _ in cleaned)
    if wants_ssl and not has_ssl:
        cleaned.append(("ssl", "require"))

    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(cleaned), parts.fragment)
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
