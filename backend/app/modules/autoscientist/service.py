"""
Adaption AutoScientist SDK Service.
Strictly aligned with official Adaption SDK v0.17.1 methods, signatures, and types:
- client.datasets.upload_file(path, name=..., processing_mode=..., column_mapping=...) -> UploadCompleteByIDResponse
- client.datasets.get_status(dataset_id=...) -> DatasetGetStatusResponse
- client.autoscientist.list_models() -> AutoscientistListModelsResponse
- client.autoscientist.recommend_hyperparams(dataset_id=..., model=...) -> AutoscientistRecommendHyperparamsResponse
- client.autoscientist.create(dataset_id=..., model=..., ...) -> AutoscientistRun
- client.autoscientist.get(experiment_id=...) -> AutoscientistRun
- client.autoscientist.download(experiment_id=...) -> BinaryAPIResponse (.write_to_file / .read)

Safe-by-default: dry_run=True prevents all billable operations, cloud executions, and uploads.
All mock outputs are explicitly flagged with is_mock=True.
Never prints or exposes ADAPTION_API_KEY.
"""
import os
import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.core.config import settings
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

logger = logging.getLogger(__name__)

# Official SDK Import
try:
    from adaption import Adaption
    from adaption.types import (
        DatasetGetStatusResponse,
        AutoscientistListModelsResponse,
        AutoscientistRecommendHyperparamsResponse,
        AutoscientistRun,
    )
    from adaption.types.datasets.upload_complete_by_id_response import UploadCompleteByIDResponse
    ADAPTION_SDK_AVAILABLE = True
except ImportError:
    ADAPTION_SDK_AVAILABLE = False
    Adaption = None


class AutoScientistService:
    """
    Programmatic client wrapper for Adaption AutoScientist SDK.
    Safe-by-default: dry_run=True prevents accidental charges, network calls, or uploads.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        dry_run: Optional[bool] = None,
        audit_dir: Optional[str] = None,
        max_retries: Optional[int] = None,
        timeout_seconds: Optional[int] = None,
    ):
        self.api_key = api_key or os.getenv("ADAPTION_API_KEY", getattr(settings, "ADAPTION_API_KEY", ""))
        self.dry_run = dry_run if dry_run is not None else getattr(settings, "ADAPTION_DRY_RUN", True)
        self.max_retries = max_retries or getattr(settings, "ADAPTION_MAX_RETRIES", 3)
        self.timeout_seconds = timeout_seconds or getattr(settings, "ADAPTION_TIMEOUT_SECONDS", 60)
        
        # Setup audit storage
        self.audit_dir = Path(audit_dir or "artifacts/training_results/autoscientist")
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize official SDK client only when live mode is requested
        self._sdk_client = None
        if not self.dry_run:
            if not ADAPTION_SDK_AVAILABLE:
                raise RuntimeError(
                    "Adaption SDK ('adaption') is not installed. "
                    "Run pip install 'adaption>=0.7.0' only after explicit user approval."
                )
            if not self.api_key:
                raise ValueError("ADAPTION_API_KEY is required to initialize live AutoScientist client.")
            self._sdk_client = Adaption(api_key=self.api_key, timeout=float(self.timeout_seconds))
            logger.info("Initialized live Adaption AutoScientist client.")
        else:
            logger.info("AutoScientist initialized in DRY-RUN mode. No billable operations will be dispatched.")

    def _execute_with_retry(self, operation_name: str, func, *args, **kwargs):
        """Execute callable with exponential backoff retry for transient errors."""
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                # Mask credentials if they inadvertently appear in error message
                err_msg = str(e)
                if self.api_key and self.api_key in err_msg:
                    err_msg = err_msg.replace(self.api_key, "[REDACTED_KEY]")
                logger.warning(
                    f"[{operation_name}] Attempt {attempt}/{self.max_retries} failed: {err_msg}"
                )
                if attempt < self.max_retries:
                    sleep_time = 2 ** (attempt - 1)
                    time.sleep(sleep_time)
        raise RuntimeError(
            f"Operation '{operation_name}' failed after {self.max_retries} attempts: {last_exception}"
        ) from last_exception

    def _persist_audit_log(self, log_type: str, record_id: str, payload: Dict[str, Any]) -> str:
        """Persist metadata JSON in artifacts directory for traceability."""
        filename = f"{log_type}_{record_id}_{int(time.time())}.json"
        filepath = self.audit_dir / filename
        data = {
            "log_type": log_type,
            "record_id": record_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": self.dry_run,
            "payload": payload,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return str(filepath)

    # --------------------------------------------------------------------------
    # 1. Dataset Upload Service
    # --------------------------------------------------------------------------
    def upload_dataset(
        self,
        file_path: str,
        name: Optional[str] = None,
        processing_mode: str = "raw",
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> DatasetUploadResponse:
        """
        Uploads a local dataset file using the official SDK method:
        client.datasets.upload_file(path=..., name=..., processing_mode=..., column_mapping=...)
        Returns UploadCompleteByIDResponse (dataset_id, status).
        """
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(f"Dataset file not found at: {file_path}")

        # Count lines for local verification
        with open(p, "r", encoding="utf-8") as f:
            row_count = sum(1 for _ in f)

        if self.dry_run:
            mock_id = f"ds_dryrun_{p.stem}_{int(time.time())}"
            response = DatasetUploadResponse(
                dataset_id=mock_id,
                status="pending",
                filename=p.name,
                row_count=row_count,
                created_at=datetime.now(timezone.utc).isoformat(),
                is_mock=True,
                message=f"[DRY-RUN] Verified file existence ({row_count} rows). No actual upload performed.",
            )
            self._persist_audit_log("dataset_upload", mock_id, response.model_dump())
            return response

        # Live SDK execution
        mapping = column_mapping or {"prompt": "prompt", "completion": "completion"}
        dataset_name = name or p.stem

        def _call_sdk():
            # Matches official SDK: client.datasets.upload_file(path, name=..., processing_mode=..., column_mapping=...)
            return self._sdk_client.datasets.upload_file(
                path=str(p.resolve()),
                name=dataset_name,
                processing_mode=processing_mode,
                column_mapping=mapping,
            )

        sdk_resp = self._execute_with_retry("upload_dataset", _call_sdk)
        ds_id = getattr(sdk_resp, "dataset_id", str(sdk_resp))
        ds_status = getattr(sdk_resp, "status", "pending")

        response = DatasetUploadResponse(
            dataset_id=ds_id,
            status=str(ds_status),
            filename=p.name,
            row_count=row_count,
            created_at=datetime.now(timezone.utc).isoformat(),
            is_mock=False,
            message="Dataset uploaded successfully via Adaption SDK.",
        )
        self._persist_audit_log("dataset_upload", ds_id, response.model_dump())
        return response

    # --------------------------------------------------------------------------
    # 2. Dataset Processing-Status Check
    # --------------------------------------------------------------------------
    def check_dataset_status(self, dataset_id: str) -> DatasetStatusResponse:
        """
        Checks processing status of an uploaded dataset using:
        client.datasets.get_status(dataset_id=...) -> DatasetGetStatusResponse
        """
        if self.dry_run:
            return DatasetStatusResponse(
                dataset_id=dataset_id,
                status=DatasetStatusEnum.SUCCEEDED,
                row_count=1050,
                progress={"percentage": 100.0, "step": "dry_run_complete"},
                error_data=None,
                is_mock=True,
            )

        def _call_sdk():
            return self._sdk_client.datasets.get_status(dataset_id=dataset_id)

        sdk_resp = self._execute_with_retry("check_dataset_status", _call_sdk)
        
        status_str = getattr(sdk_resp, "status", "pending").lower()
        status_enum_map = {
            "pending": DatasetStatusEnum.PENDING,
            "running": DatasetStatusEnum.RUNNING,
            "awaiting_input": DatasetStatusEnum.AWAITING_INPUT,
            "succeeded": DatasetStatusEnum.SUCCEEDED,
            "failed": DatasetStatusEnum.FAILED,
        }
        status_enum = status_enum_map.get(status_str, DatasetStatusEnum.PENDING)

        progress_dict = None
        if getattr(sdk_resp, "progress", None):
            prog = sdk_resp.progress
            progress_dict = {
                "step": getattr(prog, "step", None),
                "percentage": getattr(prog, "percentage", None),
            }

        error_dict = None
        if getattr(sdk_resp, "error_data", None):
            err = sdk_resp.error_data
            error_dict = {
                "code": getattr(err, "code", None),
                "message": getattr(err, "message", None),
            }

        return DatasetStatusResponse(
            dataset_id=dataset_id,
            status=status_enum,
            row_count=getattr(sdk_resp, "row_count", None),
            progress=progress_dict,
            error_data=error_dict,
            is_mock=False,
        )

    # --------------------------------------------------------------------------
    # 3. Available Model Listing
    # --------------------------------------------------------------------------
    def list_available_models(self) -> List[ModelInfo]:
        """
        Lists compatible models for AutoScientist fine-tuning using:
        client.autoscientist.list_models() -> AutoscientistListModelsResponse
        """
        if self.dry_run:
            return [
                ModelInfo(
                    id="meta-llama/Llama-3.1-8B-Instruct",
                    display_name="Llama 3.1 8B Instruct",
                    model_size="8B",
                    context_length=128000,
                    methods=["instruction", "alignment"],
                    training_types=["lora", "full"],
                    train_with_reasoning=True,
                    is_mock=True,
                ),
                ModelInfo(
                    id="Qwen/Qwen2.5-7B-Instruct",
                    display_name="Qwen 2.5 7B Instruct",
                    model_size="7.6B",
                    context_length=32768,
                    methods=["instruction"],
                    training_types=["lora"],
                    train_with_reasoning=True,
                    is_mock=True,
                ),
                ModelInfo(
                    id="mistralai/Mistral-7B-Instruct-v0.3",
                    display_name="Mistral 7B Instruct v0.3",
                    model_size="7.2B",
                    context_length=32768,
                    methods=["instruction"],
                    training_types=["lora"],
                    train_with_reasoning=False,
                    is_mock=True,
                ),
            ]

        def _call_sdk():
            return self._sdk_client.autoscientist.list_models()

        sdk_resp = self._execute_with_retry("list_available_models", _call_sdk)
        models_list = getattr(sdk_resp, "models", [])
        results = []
        for m in models_list:
            results.append(
                ModelInfo(
                    id=getattr(m, "id", str(m)),
                    display_name=getattr(m, "display_name", getattr(m, "id", "")),
                    model_size=getattr(m, "api_model_size", None),
                    context_length=getattr(m, "context_length", None),
                    methods=getattr(m, "methods", []),
                    training_types=getattr(m, "training_types", []),
                    train_with_reasoning=getattr(m, "train_with_reasoning", False),
                    is_mock=False,
                )
            )
        return results

    def verify_auth_and_list_live_models(self) -> List[ModelInfo]:
        """
        Explicit safe read-only verification method.
        Directly checks credentials against client.autoscientist.list_models()
        without enabling dataset upload, cloud training, or billable operations.
        Never prints or exposes ADAPTION_API_KEY.
        """
        if not ADAPTION_SDK_AVAILABLE:
            raise RuntimeError("Adaption SDK ('adaption') is not installed.")
        if not self.api_key:
            raise ValueError("ADAPTION_API_KEY is not configured in backend environment.")

        # Instantiate a dedicated read-only client
        client = Adaption(api_key=self.api_key, timeout=float(self.timeout_seconds))
        raw_res = client.autoscientist.list_models()
        models_list = getattr(raw_res, "models", [])
        results = []
        for m in models_list:
            results.append(
                ModelInfo(
                    id=getattr(m, "id", str(m)),
                    display_name=getattr(m, "display_name", getattr(m, "id", "")),
                    model_size=getattr(m, "api_model_size", None),
                    context_length=getattr(m, "context_length", None),
                    methods=getattr(m, "methods", []),
                    training_types=getattr(m, "training_types", []),
                    train_with_reasoning=getattr(m, "train_with_reasoning", False),
                    is_mock=False,
                )
            )
        return results

    # --------------------------------------------------------------------------
    # 4. Recommended Hyperparameter Retrieval
    # --------------------------------------------------------------------------
    def get_recommended_hyperparameters(
        self,
        dataset_id: str,
        model: Optional[str] = None
    ) -> RecommendedHyperparams:
        """
        Retrieves recommended hyperparameters using:
        client.autoscientist.recommend_hyperparams(dataset_id=..., model=...)
        """
        target_model = model or "meta-llama/Llama-3.1-8B-Instruct"

        if self.dry_run:
            return RecommendedHyperparams(
                model=target_model,
                training_type="lora",
                n_epochs=3.0,
                learning_rate=2e-5,
                batch_size=8,
                lora_r=16.0,
                lora_alpha=32.0,
                lora_dropout=0.05,
                lora_trainable_modules="all-linear",
                lr_scheduler_type="cosine",
                warmup_ratio=0.03,
                weight_decay=0.01,
                max_grad_norm=1.0,
                train_on_inputs=False,
                is_mock=True,
            )

        def _call_sdk():
            kwargs = {"dataset_id": dataset_id}
            if model:
                kwargs["model"] = model
            return self._sdk_client.autoscientist.recommend_hyperparams(**kwargs)

        sdk_resp = self._execute_with_retry("get_recommended_hyperparams", _call_sdk)
        hp = getattr(sdk_resp, "hyperparams", None)

        return RecommendedHyperparams(
            model=getattr(sdk_resp, "model", target_model),
            training_type=getattr(hp, "training_type", "lora") if hp else "lora",
            n_epochs=getattr(hp, "n_epochs", 3.0) if hp else 3.0,
            learning_rate=getattr(hp, "learning_rate", 2e-5) if hp else 2e-5,
            batch_size=getattr(hp, "batch_size", 8) if hp else 8,
            lora_r=getattr(hp, "lora_r", 16.0) if hp else 16.0,
            lora_alpha=getattr(hp, "lora_alpha", 32.0) if hp else 32.0,
            lora_dropout=getattr(hp, "lora_dropout", 0.05) if hp else 0.05,
            lora_trainable_modules=getattr(hp, "lora_trainable_modules", "all-linear") if hp else "all-linear",
            lr_scheduler_type=getattr(hp, "lr_scheduler_type", "cosine") if hp else "cosine",
            warmup_ratio=getattr(hp, "warmup_ratio", 0.03) if hp else 0.03,
            weight_decay=getattr(hp, "weight_decay", 0.01) if hp else 0.01,
            max_grad_norm=getattr(hp, "max_grad_norm", 1.0) if hp else 1.0,
            train_on_inputs=getattr(hp, "train_on_inputs", False) if hp else False,
            is_mock=False,
        )

    # --------------------------------------------------------------------------
    # 5. Training Run Creation (Requires Explicit Confirmation in Live Mode)
    # --------------------------------------------------------------------------
    def create_training_run(
        self,
        request: TrainingRunCreateRequest,
        user_confirmed_paid_operation: bool = False,
    ) -> TrainingRunResponse:
        """
        Creates an AutoScientist training run using:
        client.autoscientist.create(dataset_id=..., model=..., training_method=..., ...)
        SAFETY GUARD: In live mode, raises PermissionError unless user_confirmed_paid_operation=True.
        """
        if self.dry_run:
            mock_run_id = f"run_dryrun_{int(time.time())}"
            response = TrainingRunResponse(
                id=mock_run_id,
                dataset_id=request.dataset_id,
                model=request.model or "meta-llama/Llama-3.1-8B-Instruct",
                status=TrainingRunStatusEnum.PENDING,
                training_method=request.training_method or "instruction",
                created_at=datetime.now(timezone.utc).isoformat(),
                iterations_completed=0.0,
                max_iterations=request.max_iterations or 3.0,
                target_win_rate=request.target_win_rate or 0.85,
                download_available=False,
                is_mock=True,
            )
            self._persist_audit_log("training_run", mock_run_id, response.model_dump())
            return response

        # Live safety gate
        if not user_confirmed_paid_operation:
            raise PermissionError(
                "Execution halted: Paid operations require explicit user approval. "
                "Pass user_confirmed_paid_operation=True to initiate actual model training."
            )

        def _call_sdk():
            kwargs = {
                "dataset_id": request.dataset_id,
            }
            if request.model:
                kwargs["model"] = request.model
            if request.training_method:
                kwargs["training_method"] = request.training_method
            if request.data_format:
                kwargs["data_format"] = request.data_format
            if request.column_mapping:
                kwargs["column_mapping"] = request.column_mapping
            if request.hyperparams:
                kwargs["hyperparams"] = request.hyperparams
            if request.max_iterations is not None:
                kwargs["max_iterations"] = request.max_iterations
            if request.target_win_rate is not None:
                kwargs["target_win_rate"] = request.target_win_rate

            return self._sdk_client.autoscientist.create(**kwargs)

        sdk_run = self._execute_with_retry("create_training_run", _call_sdk)
        run_id = getattr(sdk_run, "id", str(sdk_run))

        status_raw = getattr(sdk_run, "status", "pending").lower()
        status_enum = TrainingRunStatusEnum.PENDING if status_raw == "pending" else TrainingRunStatusEnum.RUNNING

        response = TrainingRunResponse(
            id=run_id,
            dataset_id=getattr(sdk_run, "dataset_id", request.dataset_id),
            model=getattr(sdk_run, "model", request.model),
            status=status_enum,
            training_method=getattr(sdk_run, "training_method", request.training_method),
            created_at=str(getattr(sdk_run, "created_at", datetime.now(timezone.utc).isoformat())),
            iterations_completed=getattr(sdk_run, "iterations_completed", 0.0),
            max_iterations=getattr(sdk_run, "max_iterations", 3.0),
            target_win_rate=getattr(sdk_run, "target_win_rate", 0.85),
            best_win_rate=getattr(sdk_run, "best_win_rate", None),
            download_available=getattr(sdk_run, "download_available", False),
            is_mock=False,
        )
        self._persist_audit_log("training_run", run_id, response.model_dump())
        return response

    # --------------------------------------------------------------------------
    # 6. Run Status Monitoring
    # --------------------------------------------------------------------------
    def get_run_status(self, experiment_id: str) -> TrainingRunResponse:
        """
        Retrieves status of an AutoScientist run using:
        client.autoscientist.get(experiment_id=...) -> AutoscientistRun
        """
        if self.dry_run:
            return TrainingRunResponse(
                id=experiment_id,
                dataset_id="ds_dryrun_sample",
                model="meta-llama/Llama-3.1-8B-Instruct",
                status=TrainingRunStatusEnum.SUCCEEDED,
                training_method="instruction",
                created_at=datetime.now(timezone.utc).isoformat(),
                completed_at=datetime.now(timezone.utc).isoformat(),
                iterations_completed=3.0,
                max_iterations=3.0,
                target_win_rate=0.85,
                best_win_rate=0.92,
                best_hyperparams={
                    "learning_rate": 2e-5,
                    "n_epochs": 3.0,
                    "lora_r": 16.0,
                },
                download_available=True,
                is_mock=True,
            )

        def _call_sdk():
            # Matches official SDK: client.autoscientist.get(experiment_id=...)
            return self._sdk_client.autoscientist.get(experiment_id=experiment_id)

        sdk_run = self._execute_with_retry("get_run_status", _call_sdk)
        status_raw = getattr(sdk_run, "status", "running").lower()

        status_mapping = {
            "pending": TrainingRunStatusEnum.PENDING,
            "running": TrainingRunStatusEnum.RUNNING,
            "succeeded": TrainingRunStatusEnum.SUCCEEDED,
            "failed": TrainingRunStatusEnum.FAILED,
            "cancelled": TrainingRunStatusEnum.CANCELLED,
        }

        best_hp_dict = None
        if getattr(sdk_run, "best_hyperparams", None):
            hp = sdk_run.best_hyperparams
            best_hp_dict = {k: getattr(hp, k) for k in dir(hp) if not k.startswith("_") and not callable(getattr(hp, k))}

        return TrainingRunResponse(
            id=getattr(sdk_run, "id", experiment_id),
            dataset_id=getattr(sdk_run, "dataset_id", None),
            model=getattr(sdk_run, "model", None),
            status=status_mapping.get(status_raw, TrainingRunStatusEnum.RUNNING),
            training_method=getattr(sdk_run, "training_method", "instruction"),
            created_at=str(getattr(sdk_run, "created_at", datetime.now(timezone.utc).isoformat())),
            completed_at=str(getattr(sdk_run, "completed_at", "")) if getattr(sdk_run, "completed_at", None) else None,
            iterations_completed=float(getattr(sdk_run, "iterations_completed", 0.0)),
            max_iterations=float(getattr(sdk_run, "max_iterations", 3.0)),
            target_win_rate=float(getattr(sdk_run, "target_win_rate", 0.85)),
            best_win_rate=getattr(sdk_run, "best_win_rate", None),
            best_hyperparams=best_hp_dict,
            download_available=bool(getattr(sdk_run, "download_available", False)),
            error=getattr(sdk_run, "error", None),
            is_mock=False,
        )

    # --------------------------------------------------------------------------
    # 7. Checkpoint Download
    # --------------------------------------------------------------------------
    def download_best_checkpoint(
        self,
        experiment_id: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Downloads best model weights/checkpoint artifact using:
        client.autoscientist.download(experiment_id=...) -> BinaryAPIResponse
        Saves stream via response.write_to_file(destination_path).
        """
        target_dir = Path(output_dir or f"artifacts/training_results/checkpoints/{experiment_id}")
        target_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = target_dir / "checkpoint.tar.gz"

        if self.dry_run:
            # Generate simulated mock manifest for dry-run verification
            mock_manifest = target_dir / "adapter_config.json"
            mock_manifest_content = {
                "base_model_name_or_path": "meta-llama/Llama-3.1-8B-Instruct",
                "lora_alpha": 32,
                "lora_dropout": 0.05,
                "r": 16,
                "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
                "is_mock": True,
                "download_timestamp": datetime.now(timezone.utc).isoformat(),
            }
            with open(mock_manifest, "w", encoding="utf-8") as f:
                json.dump(mock_manifest_content, f, indent=2)

            return {
                "experiment_id": experiment_id,
                "output_dir": str(target_dir.resolve()),
                "status": "mock_download_completed",
                "is_mock": True,
                "files": [str(mock_manifest.name)],
            }

        def _call_sdk():
            # Matches official SDK: client.autoscientist.download(experiment_id=...)
            return self._sdk_client.autoscientist.download(experiment_id=experiment_id)

        binary_resp = self._execute_with_retry("download_best_checkpoint", _call_sdk)
        # Use official BinaryAPIResponse.write_to_file method
        binary_resp.write_to_file(str(artifact_path.resolve()))

        return {
            "experiment_id": experiment_id,
            "output_dir": str(target_dir.resolve()),
            "status": "download_completed",
            "is_mock": False,
            "files": [artifact_path.name],
        }
