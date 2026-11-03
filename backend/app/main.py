from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.db.session import engine, Base
from app.api.v1.health import router as health_router
from app.api.v1.pedagogy import router as pedagogy_router

setup_logging(debug=settings.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing NEUROTEACH AI database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully.")
    yield
    logger.info("Shutting down NEUROTEACH AI service...")

app = FastAPI(
    title="NEUROTEACH AI Pedagogical API",
    description="Backend modular monolith for NEUROTEACH AI adaptive learning platform.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )

# Routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(pedagogy_router, prefix="/api/v1", tags=["Pedagogy"])

@app.get("/")
async def root():
    return {
        "platform": "NEUROTEACH AI",
        "status": "operational",
        "docs_url": "/docs",
    }
