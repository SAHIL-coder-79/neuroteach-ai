"""
Test suite validating Stage 6.4 Training Configuration Candidate and Safety Gates.
Confirms:
1. Candidate JSON exists, matches official SDK schemas, and targets the verified dataset.
2. Safety gates prevent unauthorized paid cloud execution.
3. Live model requirements (Qwen/Qwen3.5-4B, instruction format, lora) are strictly maintained.
"""
import json
import pytest
from pathlib import Path

from app.modules.autoscientist.service import AutoScientistService
from app.modules.autoscientist.schemas import TrainingRunCreateRequest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def candidate_config():
    config_path = REPO_ROOT / "artifacts" / "training_results" / "training_config_candidate.json"
    assert config_path.exists(), f"Candidate config missing at {config_path}!"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_candidate_config_matches_uploaded_dataset(candidate_config):
    assert candidate_config["dataset_id"] == "0a290391-cf2a-47bb-9cb5-2e0cc83783ed"
    assert candidate_config["dataset_rows"] == 1080
    assert candidate_config["model"] == "Qwen/Qwen3.5-4B"
    assert candidate_config["training_method"] == "instruction"
    assert candidate_config["data_format"] == "instruction"
    assert candidate_config["column_mapping"] == {"prompt": "prompt", "completion": "completion"}


def test_candidate_hyperparameters_conform_to_recommendations(candidate_config):
    hp = candidate_config["hyperparams"]
    assert hp["training_type"] == "lora"
    assert hp["n_epochs"] == 1.0
    assert hp["learning_rate"] == 0.00005
    assert hp["batch_size"] == "max"
    assert hp["lora_r"] == 16.0
    assert hp["lora_alpha"] == 32.0
    assert hp["lr_scheduler_type"] == "cosine"


def test_candidate_safety_flags_are_enforced(candidate_config):
    safety = candidate_config["safety_status"]
    assert safety["is_dry_run"] is True
    assert safety["paid_operation_authorized"] is False
    assert safety["requires_explicit_user_approval"] is True


def test_paid_operation_safety_gate_blocks_live_execution():
    service = AutoScientistService(dry_run=True)
    req = TrainingRunCreateRequest(
        dataset_id="0a290391-cf2a-47bb-9cb5-2e0cc83783ed",
        model="Qwen/Qwen3.5-4B"
    )
    # Dry-run returns safe mock without network call
    res = service.create_training_run(req)
    assert res.is_mock is True

    # Switching to live without explicit confirmation must fail immediately
    live_service = AutoScientistService(dry_run=False, api_key="mock_key")
    with pytest.raises(PermissionError) as exc_info:
        live_service.create_training_run(req, user_confirmed_paid_operation=False)
    assert "Paid operations require explicit user approval" in str(exc_info.value)
