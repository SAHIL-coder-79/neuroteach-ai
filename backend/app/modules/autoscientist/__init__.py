"""
AutoScientist Module Init.
Exports AutoScientistService and schema definitions.
"""
from app.modules.autoscientist.service import AutoScientistService
from app.modules.autoscientist.schemas import (
    DatasetUploadResponse,
    DatasetStatusResponse,
    DatasetStatusEnum,
    ModelInfo,
    RecommendedHyperparams,
    TrainingRunCreateRequest,
    TrainingRunResponse,
    TrainingRunStatusEnum,
)

__all__ = [
    "AutoScientistService",
    "DatasetUploadResponse",
    "DatasetStatusResponse",
    "DatasetStatusEnum",
    "ModelInfo",
    "RecommendedHyperparams",
    "TrainingRunCreateRequest",
    "TrainingRunResponse",
    "TrainingRunStatusEnum",
]
