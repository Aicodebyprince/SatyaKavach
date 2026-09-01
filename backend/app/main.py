"""
SatyaKavach - Main FastAPI Application
AI-Powered Deepfake & Manipulated Media Detection Platform

सत्य (Truth) + कवच (Armor) = Armor for the Truth
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1.upload import router as upload_router
from app.api.v1.verification import router as verification_router
from app.api.v1.auth import router as auth_router

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("satyakavach")


# ── Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info(f"🛡️ {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    logger.info(f"   Demo mode: {settings.DEMO_MODE}")
    logger.info(f"   Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")

    # Create tables
    await init_db()
    logger.info("✅ Database tables created")

    yield

    # Shutdown
    await close_db()
    logger.info("👋 Shutting down")


# ── App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(verification_router, prefix="/api/v1")


# ── Health Check ─────────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "demo_mode": settings.DEMO_MODE,
    }


@app.get("/")
async def root():
    return {
        "name": "🛡️ SatyaKavach",
        "tagline": "Armor for the Truth — सत्य कवच",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": {
            "upload": "/api/v1/upload/",
            "upload_link": "/api/v1/upload/link",
            "status": "/api/v1/verification/{media_id}/status",
            "result": "/api/v1/verification/{media_id}/result",
            "history": "/api/v1/verification/history",
            "auth_register": "/api/v1/auth/register",
            "auth_login": "/api/v1/auth/login",
            "auth_anonymous": "/api/v1/auth/anonymous",
        },
    }
