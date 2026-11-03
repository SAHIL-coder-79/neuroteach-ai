import os
import json
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.modules.llm.client import PedagogicalModelClient, ModelServiceUnavailableError

@pytest.mark.asyncio
async def test_adapter_metadata_verification():
    """Verify that adapter metadata matches the winning AutoScientist experiment."""
    prov = PedagogicalModelClient.get_provenance()
    assert prov["model_name"] == "neuroteach-trained"
    assert prov["base_model"] == "togethercomputer/Qwen3.5-4B"
    assert prov["adapter_experiment_id"] == "819874ef-44b1-4a76-a049-1ce35638bba8"
    assert prov["adapter_artifacts_verified"] is True

    # Read config directly
    adapter_cfg_path = os.path.join(
        os.path.dirname(__file__), "..", "..", prov["adapter_path"], "adapter_config.json"
    )
    if not os.path.exists(adapter_cfg_path):
        adapter_cfg_path = os.path.join(
            os.path.dirname(__file__), "..", prov["adapter_path"], "adapter_config.json"
        )
    with open(adapter_cfg_path, "r") as f:
        cfg = json.load(f)
    assert cfg["r"] == 32
    assert cfg["lora_alpha"] == 64
    assert "q_proj" in cfg["target_modules"]
    assert "v_proj" in cfg["target_modules"]

@pytest.mark.asyncio
async def test_health_provenance_reporting():
    """Verify explicit model provenance in health/status output."""
    prov = PedagogicalModelClient.get_provenance()
    assert "model_name" in prov
    assert "base_model" in prov
    assert "adapter_experiment_id" in prov
    assert "adapter_path" in prov
    assert "inference_provider" in prov
    assert prov["adapter_artifacts_verified"] is True

@pytest.mark.asyncio
async def test_model_readiness_probe():
    """Verify model readiness probe reports status truthfully."""
    is_ready, msg = await PedagogicalModelClient.check_readiness()
    assert isinstance(is_ready, bool)
    assert isinstance(msg, str)
    assert len(msg) > 0

@pytest.mark.asyncio
async def test_mock_fallback_isolation_and_hard_failure(monkeypatch):
    """
    Verify that with ENABLE_MOCK_FALLBACK=False, if the inference server is unreachable,
    the client strictly raises ModelServiceUnavailableError and does NOT fall back silently.
    """
    monkeypatch.setattr(settings, "ENABLE_MOCK_FALLBACK", False)
    monkeypatch.setattr(settings, "MODEL_ENDPOINT_URL", "http://127.0.0.1:9999/v1/chat/completions")
    monkeypatch.setattr(settings, "MODEL_PROVIDER", "local_service")

    with pytest.raises(ModelServiceUnavailableError) as exc_info:
        await PedagogicalModelClient.generate_turn(
            subject="mathematics",
            concept_id="quadratic.vertex",
            question_text="Find the vertex of f(x) = x^2 - 4x + 3",
            student_message="x = -2",
            student_reasoning="x = b / (2a)",
            learner_state={},
        )
    assert "currently unavailable" in str(exc_info.value)
    assert "forbids silent mock fallback" in str(exc_info.value)

@pytest.mark.asyncio
async def test_mock_fallback_when_explicitly_enabled(monkeypatch):
    """
    Verify that when ENABLE_MOCK_FALLBACK=True (e.g. dev/offline test mode),
    fallback simulator provides valid turn structure.
    """
    monkeypatch.setattr(settings, "ENABLE_MOCK_FALLBACK", True)
    monkeypatch.setattr(settings, "MODEL_ENDPOINT_URL", "http://127.0.0.1:9999/v1/chat/completions")
    monkeypatch.setattr(settings, "MODEL_PROVIDER", "local_service")

    turn = await PedagogicalModelClient.generate_turn(
        subject="mathematics",
        concept_id="quadratic.vertex",
        question_text="Find the vertex of f(x) = x^2 - 4x + 3",
        student_message="x = -2",
        student_reasoning="x = b / (2a)",
        learner_state={},
    )
    assert "diagnosis" in turn
    assert "strategy" in turn
    assert "intervention" in turn
    assert turn["diagnosis"]["misconception_id"] == "sign_error_vertex"

@pytest.mark.asyncio
async def test_api_503_on_unavailable_inference(monkeypatch):
    """Verify pedagogy API returns 503 Service Unavailable when model is offline and fallback is disabled."""
    from app.api.v1.pedagogy import process_turn, TurnRequest

    monkeypatch.setattr(settings, "ENABLE_MOCK_FALLBACK", False)
    monkeypatch.setattr(settings, "MODEL_ENDPOINT_URL", "http://127.0.0.1:9999/v1/chat/completions")
    monkeypatch.setattr(settings, "MODEL_PROVIDER", "local_service")

    req = TurnRequest(
        subject="mathematics",
        concept_id="quadratic.vertex",
        question_text="Find the vertex of f(x) = x^2 - 4x + 3",
        canonical_answer="(2, -1)",
        student_message="x = -2",
        student_reasoning="x = b / (2a)",
    )

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await process_turn(req)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail["code"] == "MODEL_SERVICE_UNAVAILABLE"
