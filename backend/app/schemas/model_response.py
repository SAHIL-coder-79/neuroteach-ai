from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class StrategyRecord(BaseModel):
    name: str
    outcome: str # "success", "partial", "fail"
    hint_level: Optional[int] = None
    rationale: Optional[str] = None

class LearnerStateSchema(BaseModel):
    student_id: str
    concept_id: str
    mastery_score: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_count: int = 0
    active_misconceptions: List[str] = Field(default_factory=list)
    hint_level_used: int = Field(default=0, ge=0, le=3)
    attempts_on_item: int = 0
    consecutive_correct_steps: int = 0
    strategies_tried: List[StrategyRecord] = Field(default_factory=list)
    recent_accuracy: float = 0.0
    time_ratio: float = 1.0
    frustration_flag: bool = False

class NextQuestionSchema(BaseModel):
    id: str
    text: str
    pattern_id: Optional[str] = None
    difficulty: str = "medium"
    transfer_level: Optional[str] = None # near, medium, far

class MasteryEvidenceSchema(BaseModel):
    item_id: str
    transfer_level: str # near, medium, far
    credit: float = Field(ge=0.0, le=1.0)
    timestamp: str

class ModelResponseSchema(BaseModel):
    """
    Strict Pydantic schema for the pedagogical model response.
    Model output is treated as a proposal and validated by deterministic guards.
    """
    concept: str
    learner_state: LearnerStateSchema
    detected_misconception: Optional[str] = None
    misconception_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    selected_strategy: str
    explanation: str
    hint: Optional[str] = None
    next_question: Optional[NextQuestionSchema] = None
    expected_answer: Optional[str] = None
    visualization_spec: Optional[Dict[str, Any]] = None
    answer_revealed: bool = False
    mastery_evidence: Optional[MasteryEvidenceSchema] = None
