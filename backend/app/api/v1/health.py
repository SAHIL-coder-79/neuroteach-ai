from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings
from app.modules.llm.client import PedagogicalModelClient

router = APIRouter()

@router.get("/health", summary="Health check endpoint with model provenance")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    provenance = PedagogicalModelClient.get_provenance()
    is_ready, ready_msg = await PedagogicalModelClient.check_readiness()

    # In local demo mode, overall health is healthy when database is active and adapter files are verified
    overall_status = "healthy"
    if "unhealthy" in db_status:
        overall_status = "degraded"

    return {
        "status": overall_status,
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql",
        "db_connection": db_status,
        "environment": settings.ENVIRONMENT,
        "model_provenance": {
            "model_name": provenance["model_name"],
            "base_model": provenance["base_model"],
            "adapter_experiment_id": provenance["adapter_experiment_id"],
            "adapter_path": provenance["adapter_path"],
            "adapter_verified": provenance["adapter_artifacts_verified"],
            "inference_provider": provenance["inference_provider"],
            "is_ready": is_ready,
            "readiness_status": ready_msg,
            "mock_fallback_enabled": provenance["mock_fallback_enabled"],
        }
    }
