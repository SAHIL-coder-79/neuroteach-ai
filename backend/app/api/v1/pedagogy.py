from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.modules.visual.patterns import PatternLibrary
from app.modules.visual.validator import VisualSpecValidator
from app.modules.misconceptions.engine import MisconceptionDNAEngine
from app.modules.misconceptions.catalog import MISCONCEPTION_CATALOG
from app.modules.policy.engine import TeachingPolicyEngine
from app.modules.transfer.engine import TransferProofEngine, EvidenceItem
from app.modules.llm.client import PedagogicalModelClient, ModelServiceUnavailableError

router = APIRouter()

class TurnRequest(BaseModel):
    subject: str = "mathematics"
    concept_id: str = "quadratic.vertex"
    question_text: str
    canonical_answer: str
    student_message: str
    student_reasoning: str = ""
    learner_state: Dict[str, Any] = Field(default_factory=dict)

class ValidateSpecRequest(BaseModel):
    spec: Dict[str, Any]
    canonical_answer: str = ""

@router.post("/turn", summary="Process a pedagogical tutoring dialogue turn")
async def process_turn(req: TurnRequest):
    # 1. Obtain proposed turn from pedagogical model
    try:
        model_turn = await PedagogicalModelClient.generate_turn(
            subject=req.subject,
            concept_id=req.concept_id,
            question_text=req.question_text,
            student_message=req.student_message,
            student_reasoning=req.student_reasoning,
            learner_state=req.learner_state,
        )
    except ModelServiceUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "MODEL_SERVICE_UNAVAILABLE",
                "message": str(exc),
            }
        )

    # 2. Check deterministic guardrail: Answer Leakage
    intervention = model_turn.get("intervention", {}).get("text", "")
    is_leaking = TeachingPolicyEngine.detect_answer_leakage(intervention, req.canonical_answer)
    if is_leaking:
        # Fallback to sanitized hint ladder step
        model_turn["intervention"]["text"] = "Remember to review the definition of the formula and check the signs."

    # 3. Classify error via Misconception DNA consensus
    diag = model_turn.get("diagnosis", {})
    err_type, mis_id, conf, exp = MisconceptionDNAEngine.classify_error(
        model_prediction=diag.get("misconception_id"),
        model_confidence=diag.get("confidence", 0.5),
        submitted_answer=req.student_message,
        reasoning_text=req.student_reasoning,
        solved_recently=False,
    )
    model_turn["diagnosis"]["error_type"] = err_type
    model_turn["diagnosis"]["confidence"] = conf

    return model_turn

@router.post("/visual/validate", summary="Deterministic 7-step SymPy validation of visual_spec")
async def validate_visual_spec(req: ValidateSpecRequest):
    is_valid, errors = VisualSpecValidator.validate_spec(req.spec, req.canonical_answer)
    return {
        "is_valid": is_valid,
        "errors": errors,
        "status": "passed" if is_valid else "rejected"
    }

@router.get("/visual/similar-question", summary="Generate a solver-verified similar question")
async def generate_similar_question(
    pattern_id: str = "parabola_vertex",
    difficulty: str = "medium"
):
    if pattern_id == "parabola_vertex":
        question_data = PatternLibrary.generate_parabola_vertex_question(difficulty=difficulty)
        # Validate deterministically before returning
        is_valid, errors = VisualSpecValidator.validate_spec(question_data["visual_spec"])
        question_data["validation_status"] = "passed" if is_valid else "failed"
        return question_data

    raise HTTPException(status_code=404, detail=f"Pattern {pattern_id} not implemented yet.")

@router.get("/evaluator/misconceptions", summary="Get catalog of misconceptions")
async def list_misconceptions():
    return list(MISCONCEPTION_CATALOG.values())
