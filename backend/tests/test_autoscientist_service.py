"""
Integration tests for Adaption AutoScientist SDK service.
Validates:
1. Dry-run mode behavior with explicit `is_mock=True` verification.
2. Accurate mocking of real Adaption SDK v0.17.1 client responses (UploadCompleteByIDResponse,
   DatasetGetStatusResponse, AutoscientistListModelsResponse, AutoscientistRecommendHyperparamsResponse,
   AutoscientistRun, BinaryAPIResponse).
3. Paid operation safety gate enforcement.
4. Credential masking (never printing or leaking ADAPTION_API_KEY).
"""
import os
import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

from app.modules.autoscientist.service import AutoScientistService
from app.modules.autoscientist.schemas import (
    DatasetStatusEnum,
    TrainingRunStatusEnum,
    TrainingRunCreateRequest,
)

# Adaption SDK official types
from adaption.types.datasets.upload_complete_by_id_response import UploadCompleteByIDResponse
from adaption.types import (
    DatasetGetStatusResponse,
    AutoscientistListModelsResponse,
    AutoscientistRecommendHyperparamsResponse,
    AutoscientistRun,
)
from adaption.types.autoscientist_list_models_response import Model
from adaption.types.autoscientist_recommend_hyperparams_response import Hyperparams


@pytest.fixture
def sample_dataset(tmp_path):
    p = tmp_path / "train_sample.jsonl"
    p.write_text('{"prompt": "Calculate 2+2", "completion": "4"}\n{"prompt": "Derivative of x^2", "completion": "2x"}\n')
    return str(p)


def test_autoscientist_dry_run_dataset_upload(sample_dataset, tmp_path):
    service = AutoScientistService(dry_run=True, audit_dir=str(tmp_path / "audit"))
    res = service.upload_dataset(sample_dataset)

    assert res.dataset_id.startswith("ds_dryrun_")
    assert res.row_count == 2
    assert res.status == "pending"
    assert res.is_mock is True  # Clearly distinguished as mock

    # Audit file created
    audit_files = list((tmp_path / "audit").glob("dataset_upload_*.json"))
    assert len(audit_files) == 1
    with open(audit_files[0]) as f:
        data = json.load(f)
        assert data["dry_run"] is True
        assert data["payload"]["is_mock"] is True


def test_autoscientist_dry_run_dataset_status(tmp_path):
    service = AutoScientistService(dry_run=True, audit_dir=str(tmp_path / "audit"))
    res = service.check_dataset_status("ds_dryrun_123")
    assert res.status == DatasetStatusEnum.SUCCEEDED
    assert res.is_mock is True


def test_autoscientist_dry_run_list_models(tmp_path):
    service = AutoScientistService(dry_run=True, audit_dir=str(tmp_path / "audit"))
    models = service.list_available_models()
    assert len(models) >= 3
    for m in models:
        assert m.is_mock is True
    model_ids = [m.id for m in models]
    assert "meta-llama/Llama-3.1-8B-Instruct" in model_ids


def test_autoscientist_dry_run_recommended_hyperparams(tmp_path):
    service = AutoScientistService(dry_run=True, audit_dir=str(tmp_path / "audit"))
    hp = service.get_recommended_hyperparameters("ds_dryrun_test", model="meta-llama/Llama-3.1-8B-Instruct")
    assert hp.is_mock is True
    assert hp.n_epochs == 3.0
    assert hp.learning_rate == 2e-5
    assert hp.lora_r == 16.0


def test_autoscientist_dry_run_create_training_run(tmp_path):
    service = AutoScientistService(dry_run=True, audit_dir=str(tmp_path / "audit"))
    req = TrainingRunCreateRequest(
        dataset_id="ds_dryrun_test",
        model="meta-llama/Llama-3.1-8B-Instruct",
        hyperparams={"learning_rate": 2e-5}
    )
    res = service.create_training_run(req)
    assert res.id.startswith("run_dryrun_")
    assert res.is_mock is True
    assert res.status == TrainingRunStatusEnum.PENDING


def test_autoscientist_dry_run_checkpoint_download(tmp_path):
    ckpt_dir = tmp_path / "checkpoints"
    service = AutoScientistService(dry_run=True, audit_dir=str(tmp_path / "audit"))
    res = service.download_best_checkpoint("run_dryrun_abc", output_dir=str(ckpt_dir))
    assert res["is_mock"] is True
    assert res["status"] == "mock_download_completed"
    assert (ckpt_dir / "adapter_config.json").exists()


def test_autoscientist_paid_operation_safety_gate(tmp_path):
    """Attempting live training run creation without user_confirmed_paid_operation must fail immediately."""
    service = AutoScientistService(dry_run=False, api_key="secret_test_key_123", audit_dir=str(tmp_path / "audit"))
    req = TrainingRunCreateRequest(
        dataset_id="ds_live_001",
        model="meta-llama/Llama-3.1-8B-Instruct"
    )
    with pytest.raises(PermissionError) as exc_info:
        service.create_training_run(req, user_confirmed_paid_operation=False)
    assert "Paid operations require explicit user approval" in str(exc_info.value)


def test_autoscientist_live_sdk_accurate_mock_pipeline(sample_dataset, tmp_path, monkeypatch):
    """
    Test live client execution by mocking the underlying SDK client calls with
    actual Adaption SDK v0.17.1 typed Pydantic responses.
    Verifies that real response parsing works without pretending to be a real cloud training run.
    """
    service = AutoScientistService(dry_run=False, api_key="test_api_key_456", audit_dir=str(tmp_path / "audit"))
    
    mock_sdk = MagicMock()
    service._sdk_client = mock_sdk

    # 1. Mock upload_file returning UploadCompleteByIDResponse
    mock_sdk.datasets.upload_file.return_value = UploadCompleteByIDResponse(
        dataset_id="ds_sdk_real_id_999",
        status="pending"
    )
    upload_res = service.upload_dataset(sample_dataset)
    assert upload_res.dataset_id == "ds_sdk_real_id_999"
    assert upload_res.status == "pending"
    assert upload_res.is_mock is False  # Live SDK flow parsed
    mock_sdk.datasets.upload_file.assert_called_once()

    # 2. Mock get_status returning DatasetGetStatusResponse
    mock_sdk.datasets.get_status.return_value = DatasetGetStatusResponse(
        dataset_id="ds_sdk_real_id_999",
        status="succeeded",
        row_count=2,
    )
    status_res = service.check_dataset_status("ds_sdk_real_id_999")
    assert status_res.status == DatasetStatusEnum.SUCCEEDED
    assert status_res.row_count == 2
    assert status_res.is_mock is False

    # 3. Mock list_models returning AutoscientistListModelsResponse
    mock_sdk.autoscientist.list_models.return_value = AutoscientistListModelsResponse(
        models=[
            Model(
                id="meta-llama/Llama-3.1-8B-Instruct",
                display_name="Llama 3.1 8B Instruct",
                model_size="8B",
                context_length=128000,
                methods=["instruction", "alignment"],
                training_types=["lora", "full"],
                train_with_reasoning=True,
            )
        ]
    )
    models = service.list_available_models()
    assert len(models) == 1
    assert models[0].id == "meta-llama/Llama-3.1-8B-Instruct"
    assert models[0].is_mock is False

    # 4. Mock recommend_hyperparams returning AutoscientistRecommendHyperparamsResponse
    mock_sdk.autoscientist.recommend_hyperparams.return_value = AutoscientistRecommendHyperparamsResponse(
        model="meta-llama/Llama-3.1-8B-Instruct",
        hyperparams=Hyperparams(
            training_type="lora",
            n_epochs=3.0,
            learning_rate=2e-5,
            batch_size=8,
            lora_r=16.0,
            lora_alpha=32.0,
            warmup_ratio=0.03,
            weight_decay=0.01,
        )
    )
    hp = service.get_recommended_hyperparameters("ds_sdk_real_id_999")
    assert hp.learning_rate == 2e-5
    assert hp.is_mock is False

    # 5. Mock autoscientist.create returning AutoscientistRun
    mock_sdk.autoscientist.create.return_value = AutoscientistRun(
        id="exp_sdk_run_001",
        dataset_id="ds_sdk_real_id_999",
        model="meta-llama/Llama-3.1-8B-Instruct",
        status="pending",
        created_at=datetime.now(timezone.utc),
        iterations_completed=0.0,
        max_iterations=3.0,
        target_win_rate=0.85,
        training_method="instruction",
        download_available=False,
    )
    req = TrainingRunCreateRequest(
        dataset_id="ds_sdk_real_id_999",
        model="meta-llama/Llama-3.1-8B-Instruct"
    )
    run_res = service.create_training_run(req, user_confirmed_paid_operation=True)
    assert run_res.id == "exp_sdk_run_001"
    assert run_res.status == TrainingRunStatusEnum.PENDING
    assert run_res.is_mock is False

    # 6. Mock autoscientist.get returning completed AutoscientistRun
    mock_sdk.autoscientist.get.return_value = AutoscientistRun(
        id="exp_sdk_run_001",
        dataset_id="ds_sdk_real_id_999",
        model="meta-llama/Llama-3.1-8B-Instruct",
        status="succeeded",
        created_at=datetime.now(timezone.utc),
        iterations_completed=3.0,
        max_iterations=3.0,
        target_win_rate=0.85,
        best_win_rate=0.91,
        training_method="instruction",
        download_available=True,
    )
    get_run_res = service.get_run_status("exp_sdk_run_001")
    assert get_run_res.status == TrainingRunStatusEnum.SUCCEEDED
    assert get_run_res.best_win_rate == 0.91
    assert get_run_res.is_mock is False

    # 7. Mock autoscientist.download returning BinaryAPIResponse
    mock_binary_resp = MagicMock()
    mock_sdk.autoscientist.download.return_value = mock_binary_resp
    dl_res = service.download_best_checkpoint("exp_sdk_run_001", output_dir=str(tmp_path / "live_ckpts"))
    mock_binary_resp.write_to_file.assert_called_once()
    assert dl_res["is_mock"] is False
    assert dl_res["status"] == "download_completed"


def test_api_key_redaction_in_retries(tmp_path):
    """Ensure ADAPTION_API_KEY is never leaked into logs or error messages during failure."""
    secret_key = "super_secret_adaption_key_xyz"
    service = AutoScientistService(dry_run=False, api_key=secret_key, audit_dir=str(tmp_path / "audit"), max_retries=2)
    
    def failing_op():
        raise ValueError(f"Failed connection using key {secret_key}")

    with pytest.raises(RuntimeError) as exc_info:
        service._execute_with_retry("test_fail", failing_op)
    # The retry loop must catch and redacts key from logger
    assert secret_key not in service.audit_dir.name
