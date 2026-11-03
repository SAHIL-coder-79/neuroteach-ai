import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
import httpx
from pydantic import BaseModel, Field

from app.core.config import settings
from app.modules.misconceptions.catalog import MISCONCEPTION_CATALOG
from app.modules.policy.engine import TEACHING_STRATEGIES

logger = logging.getLogger("neuroteach.llm")

class ModelServiceUnavailableError(RuntimeError):
    """Raised when the fine-tuned inference service is offline or unreachable and fallback is disabled."""
    pass

class PedagogicalModelClient:
    """
    Production LLM Client for NEUROTEACH AI (PRD Sections 14, 15, and Stage 8).
    Connects to the real fine-tuned LoRA model (neuroteach-trained) via HTTP inference endpoint
    or Adaption Cloud Response API.
    
    Guarantees:
    - Never leaks secret keys or credentials in exceptions or responses.
    - Explicit provenance reporting (base model, experiment ID, adapter path, provider).
    - Hard failure with ModelServiceUnavailableError when model is down and fallback is disabled.
    """

    @classmethod
    def get_provenance(cls) -> Dict[str, Any]:
        """Returns metadata detailing the trained model origin, adapter, and serving configuration."""
        # Resolve relative to project root (D:\oracathon) or backend or absolute
        raw_path = settings.MODEL_ADAPTER_PATH
        if os.path.isabs(raw_path):
            adapter_path_resolved = raw_path
        else:
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
            )
            candidate1 = os.path.join(project_root, raw_path)
            candidate2 = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")), raw_path)
            adapter_path_resolved = candidate1 if os.path.exists(candidate1) else candidate2
        adapter_exists = os.path.exists(adapter_path_resolved)
        weights_exist = os.path.exists(os.path.join(adapter_path_resolved, "adapter_model.safetensors"))
        config_exists = os.path.exists(os.path.join(adapter_path_resolved, "adapter_config.json"))

        return {
            "model_name": settings.MODEL_NAME,
            "base_model": settings.MODEL_BASE_NAME,
            "adapter_experiment_id": settings.MODEL_ADAPTER_EXPERIMENT_ID,
            "adapter_path": settings.MODEL_ADAPTER_PATH,
            "adapter_artifacts_verified": adapter_exists and weights_exist and config_exists,
            "inference_provider": settings.MODEL_PROVIDER,
            "inference_endpoint": settings.MODEL_ENDPOINT_URL if settings.MODEL_PROVIDER != "adaption_cloud" else "https://api.prod.adaptionlabs.ai/api/v1/responses",
            "mock_fallback_enabled": settings.ENABLE_MOCK_FALLBACK,
        }

    @classmethod
    async def check_readiness(cls) -> Tuple[bool, str]:
        """
        Actively probes the inference server to verify the model is loaded and ready.
        Returns (is_ready, message_or_error).
        """
        prov = cls.get_provenance()
        if not prov["adapter_artifacts_verified"]:
            return False, f"Adapter checkpoint files missing at {settings.MODEL_ADAPTER_PATH}"

        if settings.MODEL_PROVIDER == "adaption_cloud":
            # Probe cloud SDK readiness
            if not settings.ADAPTION_API_KEY:
                return False, "ADAPTION_API_KEY is not configured"
            try:
                import adaption
                client = adaption.AsyncAdaption(
                    api_key=settings.ADAPTION_API_KEY,
                    base_url=settings.ADAPTION_BASE_URL or None,
                    timeout=settings.MODEL_TIMEOUT_SECONDS,
                )
                models = await client.models.list()
                return True, f"Adaption cloud connected ({len(models.data)} models available)"
            except Exception as e:
                logger.warning(f"Adaption cloud readiness check failed: {type(e).__name__}")
                return False, f"Adaption cloud unavailable: {type(e).__name__}"

        # Probe HTTP inference endpoint (e.g. vLLM, Triton, or custom FastAPI serving container)
        health_urls = [
            settings.MODEL_ENDPOINT_URL.replace("/v1/chat/completions", "/health"),
            settings.MODEL_ENDPOINT_URL.replace("/v1/chat/completions", "/v1/models"),
            settings.MODEL_ENDPOINT_URL.replace("/chat/completions", "/health"),
        ]

        async with httpx.AsyncClient(timeout=3.0) as client:
            headers = {}
            if settings.MODEL_API_KEY:
                headers["Authorization"] = f"Bearer {settings.MODEL_API_KEY}"

            last_err = None
            for url in health_urls:
                try:
                    res = await client.get(url, headers=headers)
                    if res.status_code in (200, 204):
                        return True, f"Inference server responsive at {url}"
                except Exception as ex:
                    last_err = ex

            return False, f"Inference endpoint unreachable at {settings.MODEL_ENDPOINT_URL} ({type(last_err).__name__ if last_err else 'connection refused'})"

    @classmethod
    async def generate_turn(
        cls,
        subject: str,
        concept_id: str,
        question_text: str,
        student_message: str,
        student_reasoning: Optional[str],
        learner_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Dispatches inference request to the fine-tuned model and returns structured pedagogical turn JSON.
        Throws ModelServiceUnavailableError if unreachable when mock fallback is disabled.
        """
        # Format input prompt matching the AutoScientist training dataset schema
        input_payload = {
            "task": "teach_turn",
            "subject": subject,
            "concept_id": concept_id,
            "question": {
                "id": f"q_{concept_id}",
                "text": question_text,
                "pattern_id": concept_id.replace(".", "_"),
                "visual_spec": None,
            },
            "student_attempt": {
                "answer": student_message,
                "reasoning": student_reasoning or "",
                "correct": False,
            },
            "learner_state": {
                "mastery": learner_state.get("mastery", 0.5),
                "active_misconceptions": learner_state.get("active_misconceptions", []),
                "hint_level_used": learner_state.get("hint_level_used", 1),
                "strategies_tried": learner_state.get("strategies_tried", []),
                "recent_accuracy": learner_state.get("recent_accuracy", 0.5),
            },
        }

        # Attempt real inference
        inference_success = False
        response_dict = None
        error_reason = None

        if settings.MODEL_PROVIDER == "adaption_cloud" and settings.ADAPTION_API_KEY:
            try:
                import adaption
                client = adaption.AsyncAdaption(
                    api_key=settings.ADAPTION_API_KEY,
                    base_url=settings.ADAPTION_BASE_URL or None,
                    timeout=settings.MODEL_TIMEOUT_SECONDS,
                )
                resp = await client.responses.create(
                    model=settings.MODEL_NAME,
                    instructions="You are the NeuroTeach Pedagogical Engine. Respond strictly in valid JSON matching {diagnosis, strategy, intervention, visual_spec, next_check}.",
                    input=json.dumps(input_payload),
                )
                if resp and resp.output_text:
                    response_dict = json.loads(resp.output_text)
                    inference_success = True
            except Exception as e:
                error_reason = f"Adaption cloud inference error: {type(e).__name__}"
                logger.error(f"Inference failure ({settings.MODEL_PROVIDER}): {type(e).__name__} - {str(e)}")
        else:
            # Standard OpenAI-compatible HTTP POST (vLLM / HuggingFace TGI / custom server)
            try:
                async with httpx.AsyncClient(timeout=settings.MODEL_TIMEOUT_SECONDS) as http_client:
                    headers = {"Content-Type": "application/json"}
                    if settings.MODEL_API_KEY:
                        headers["Authorization"] = f"Bearer {settings.MODEL_API_KEY}"

                    body = {
                        "model": settings.MODEL_NAME,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are the NeuroTeach Pedagogical Engine. Respond strictly in valid JSON matching {diagnosis, strategy, intervention, visual_spec, next_check}."
                            },
                            {
                                "role": "user",
                                "content": json.dumps(input_payload)
                            }
                        ],
                        "temperature": 0.2,
                        "max_tokens": 512,
                    }

                    res = await http_client.post(settings.MODEL_ENDPOINT_URL, json=body, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        content = data["choices"][0]["message"]["content"]
                        response_dict = json.loads(content)
                        inference_success = True
                    else:
                        error_reason = f"HTTP {res.status_code} from endpoint {settings.MODEL_ENDPOINT_URL}"
                        logger.error(f"Endpoint returned HTTP {res.status_code}")
            except Exception as ex:
                error_reason = f"Connection failed to {settings.MODEL_ENDPOINT_URL}: {type(ex).__name__}"
                logger.error(f"Inference connection failure: {type(ex).__name__} ({str(ex)})")

        if inference_success and response_dict:
            # Validate output keys
            if "diagnosis" in response_dict and "strategy" in response_dict and "intervention" in response_dict:
                return response_dict
            else:
                logger.warning(f"Inference response malformed: missing expected keys in {list(response_dict.keys())}")

        # If real inference fails:
        if not settings.ENABLE_MOCK_FALLBACK:
            # Hard refusal in production/demo mode
            logger.error(f"Trained model inference unavailable and mock fallback is DISABLED. Reason: {error_reason}")
            raise ModelServiceUnavailableError(
                f"Trained model service '{settings.MODEL_NAME}' is currently unavailable. "
                f"Production mode forbids silent mock fallback. Reason: {error_reason}"
            )

        # Fallback ONLY if explicitly enabled
        logger.warning(f"Falling back to deterministic pedagogical simulator (ENABLE_MOCK_FALLBACK=True). Reason: {error_reason}")
        return cls._simulate_fallback_turn(
            concept_id=concept_id,
            student_message=student_message,
            student_reasoning=student_reasoning,
            learner_state=learner_state,
        )

    @classmethod
    def _simulate_fallback_turn(
        cls,
        concept_id: str,
        student_message: str,
        student_reasoning: Optional[str],
        learner_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Deterministic offline fallback simulator adhering to strict PRD Section 15 schemas."""
        detected_misconception = None
        for mis_id, item in MISCONCEPTION_CATALOG.items():
            if item.concept_id == concept_id:
                detected_misconception = item
                break

        if not detected_misconception:
            detected_misconception = MISCONCEPTION_CATALOG["sign_error_vertex"]

        strategies_tried = learner_state.get("strategies_tried", [])
        failed_strategies = [s.get("name") for s in strategies_tried if s.get("outcome") == "fail"]

        chosen_strategy = "progressive_hint"
        if "progressive_hint" in failed_strategies:
            chosen_strategy = "counterexample"
        elif "counterexample" in failed_strategies:
            chosen_strategy = "simpler_prerequisite"

        intervention_text = f"Notice that in the formula x = -b / (2a), the leading minus sign flips the sign of b. What happens when b is negative?"

        return {
            "diagnosis": {
                "error_type": "conceptual",
                "misconception_id": detected_misconception.id,
                "confidence": 0.85,
                "evidence": student_reasoning or student_message,
                "root_concepts": detected_misconception.root_concepts,
                "explanation": detected_misconception.description,
            },
            "strategy": {
                "name": chosen_strategy,
                "rationale": "Adaptive policy selected based on previous strategy failure state.",
                "hint_level": 2 if chosen_strategy == "progressive_hint" else None,
            },
            "intervention": {
                "text": intervention_text,
                "asks_student_to": "substitute b into the negated numerator",
            },
            "visual_spec": None,
            "next_check": {"type": "observe_reply"}
        }

# Maintain backwards compatibility
MockPedagogicalModelClient = PedagogicalModelClient
