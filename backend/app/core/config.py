from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    ENVIRONMENT: str = Field(default="development", description="Runtime environment")
    DEBUG: bool = Field(default=True, description="Debug mode")
    PORT: int = Field(default=8000, description="Server port")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./neuroteach.db",
        description="Async database connection string"
    )
    
    # Security
    JWT_SECRET_KEY: str = Field(
        default="insecure_dev_secret_key_change_in_production_32bytes",
        description="JWT HMAC secret key"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="Access token expiration")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration")
    
    # AutoScientist / Model Inference Endpoint (Server-side only)
    MODEL_PROVIDER: str = Field(
        default="local_service", # "local_service", "adaption_cloud", or "vllm"
        description="Inference provider backend"
    )
    MODEL_ENDPOINT_URL: str = Field(
        default="http://localhost:8080/v1/chat/completions",
        description="Pedagogical LLM endpoint"
    )
    MODEL_NAME: str = Field(
        default="neuroteach-trained",
        description="Serving model name / adapter alias"
    )
    MODEL_BASE_NAME: str = Field(
        default="togethercomputer/Qwen3.5-4B",
        description="Base foundational model name"
    )
    MODEL_ADAPTER_EXPERIMENT_ID: str = Field(
        default="819874ef-44b1-4a76-a049-1ce35638bba8",
        description="AutoScientist LoRA experiment ID"
    )
    MODEL_ADAPTER_PATH: str = Field(
        default="artifacts/training_results/checkpoints/819874ef-44b1-4a76-a049-1ce35638bba8",
        description="Local path to checkpoint adapter"
    )
    MODEL_API_KEY: str = Field(default="", description="Secret API key for model service")
    MODEL_TIMEOUT_SECONDS: int = Field(default=15, description="Model timeout")
    MODEL_MAX_RETRIES: int = Field(default=2, description="Max retry attempts for inference")
    ENABLE_MOCK_FALLBACK: bool = Field(
        default=True,
        description="Allow deterministic pedagogical engine fallback if remote inference endpoint is offline."
    )

    # Adaption AutoScientist SDK Configuration (Server-side only - Never expose to frontend)
    ADAPTION_API_KEY: str = Field(default="", description="Secret API key for Adaption AutoScientist")
    ADAPTION_BASE_URL: str = Field(default="", description="Optional custom base URL for Adaption SDK")
    ADAPTION_DRY_RUN: bool = Field(default=True, description="Enable safe dry-run mode for AutoScientist operations")
    ADAPTION_MAX_RETRIES: int = Field(default=3, description="Retry attempts for transient failures")
    ADAPTION_TIMEOUT_SECONDS: int = Field(default=60, description="SDK client timeout in seconds")

settings = Settings()
