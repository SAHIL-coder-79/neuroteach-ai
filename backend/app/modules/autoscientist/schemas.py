"""
AutoScientist Schema Definitions.
Strictly matches the official Adaption SDK (v0.17.1) types and schemas:
- UploadCompleteByIDResponse
- DatasetGetStatusResponse
- AutoscientistListModelsResponse (Model)
- AutoscientistRecommendHyperparamsResponse (Hyperparams)
- AutoscientistRun
"""
from typing import List, Optional, Dict, Any, Union, Literal
from enum import Enum
from pydantic import BaseModel, Field


class DatasetStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_INPUT = "awaiting_input"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TrainingRunStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DatasetUploadResponse(BaseModel):
    dataset_id: str = Field(..., description="Unique dataset identifier from AutoScientist")
    status: str = Field(..., description="Status string returned by upload completion (e.g. pending)")
    filename: str
    row_count: Optional[int] = None
    created_at: str
    is_mock: bool = Field(default=False, description="Explicit flag indicating mock/dry-run vs real SDK response")
    message: Optional[str] = None


class DatasetStatusResponse(BaseModel):
    dataset_id: str
    status: DatasetStatusEnum
    row_count: Optional[int] = None
    progress: Optional[Dict[str, Any]] = None
    error_data: Optional[Dict[str, Any]] = None
    is_mock: bool = Field(default=False, description="Explicit flag indicating mock/dry-run vs real SDK response")


class ModelInfo(BaseModel):
    id: str = Field(..., description="Official model ID (e.g. meta-llama/Llama-3.1-8B-Instruct)")
    display_name: str
    model_size: Optional[str] = None
    context_length: Optional[float] = None
    methods: List[str] = Field(default_factory=list)
    training_types: List[str] = Field(default_factory=list)
    train_with_reasoning: bool = False
    is_mock: bool = Field(default=False, description="Explicit flag indicating mock/dry-run vs real SDK response")


class RecommendedHyperparams(BaseModel):
    model: str
    training_type: Optional[str] = "lora"
    n_epochs: Optional[float] = 3.0
    learning_rate: Optional[float] = 2e-5
    batch_size: Optional[Union[int, str]] = 8
    lora_r: Optional[float] = 16.0
    lora_alpha: Optional[float] = 32.0
    lora_dropout: Optional[float] = 0.05
    lora_trainable_modules: Optional[str] = "all-linear"
    lr_scheduler_type: Optional[str] = "cosine"
    warmup_ratio: Optional[float] = 0.03
    weight_decay: Optional[float] = 0.01
    max_grad_norm: Optional[float] = 1.0
    train_on_inputs: Optional[bool] = False
    custom_options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_mock: bool = Field(default=False, description="Explicit flag indicating mock/dry-run vs real SDK response")


class TrainingRunCreateRequest(BaseModel):
    dataset_id: str
    model: Optional[str] = None
    training_method: Optional[Literal["instruction", "alignment"]] = "instruction"
    data_format: Optional[Literal["chat", "instruction"]] = "instruction"
    column_mapping: Optional[Dict[str, str]] = None
    hyperparams: Optional[Dict[str, Any]] = None
    max_iterations: Optional[float] = 3.0
    target_win_rate: Optional[float] = 0.85
    run_name: Optional[str] = None


class TrainingRunResponse(BaseModel):
    id: str = Field(..., description="AutoScientist run/experiment identifier (matches AutoscientistRun.id)")
    dataset_id: Optional[str] = None
    model: Optional[str] = None
    status: TrainingRunStatusEnum
    training_method: Optional[str] = "instruction"
    created_at: str
    completed_at: Optional[str] = None
    iterations_completed: float = 0.0
    max_iterations: float = 3.0
    target_win_rate: float = 0.85
    best_win_rate: Optional[float] = None
    best_hyperparams: Optional[Dict[str, Any]] = None
    column_mapping: Optional[Dict[str, Any]] = None
    download_available: bool = False
    error: Optional[str] = None
    is_mock: bool = Field(default=False, description="Explicit flag indicating mock/dry-run vs real SDK response")
