from datetime import datetime
from typing import Dict, Any, Optional

from app.schemas.model_response import (
    ModelResponseSchema,
    LearnerStateSchema,
    NextQuestionSchema,
    MasteryEvidenceSchema,
)
from app.modules.misconceptions.catalog import MISCONCEPTION_CATALOG
from app.modules.misconceptions.engine import MisconceptionDNAEngine
from app.modules.policy.adaptive_engine import AdaptiveTeachingEngine
from app.modules.learner.manager import LearnerStateManager
from app.modules.session.manager import TeachingSessionManager
from app.modules.transfer.generator import TransferProofGenerator
from app.modules.visual.validator import VisualSpecValidator

class PedagogicalCoreOrchestrator:
    """
    Pedagogical Core Service:
    Coordinates Misconception DNA, Adaptive Teaching Engine, TransferProof,
    Learner State, and Teaching Session Management while strictly separating
    business logic from model inference proposals.
    """

    def __init__(self):
        self.learner_manager = LearnerStateManager()
        self.session_manager = TeachingSessionManager()

    def process_student_turn(
        self,
        session_id: str,
        student_id: str,
        concept_id: str,
        student_answer: str,
        student_reasoning: Optional[str],
        canonical_answer: str,
        hint_ladder: list[str],
        raw_model_proposal: Optional[Dict[str, Any]] = None,
    ) -> ModelResponseSchema:
        # 1. Fetch current learner state
        learner_state = self.learner_manager.get_or_create_state(student_id, concept_id)

        # 2. Check correctness deterministically
        is_correct = student_answer.strip() == canonical_answer.strip()

        # Update learner state with attempt
        learner_state = self.learner_manager.record_attempt(
            student_id=student_id,
            concept_id=concept_id,
            is_correct=is_correct,
        )

        detected_misconception_id = None
        misconception_conf = 0.0

        if not is_correct:
            # 3. Misconception DNA error classification
            # Treat model proposal confidence as an estimate, not ground truth
            model_conf_estimate = 0.85
            if raw_model_proposal and "misconception_confidence" in raw_model_proposal:
                model_conf_estimate = float(raw_model_proposal["misconception_confidence"])

            proposed_mis = "sign_error_vertex"
            if raw_model_proposal and raw_model_proposal.get("detected_misconception"):
                proposed_mis = raw_model_proposal["detected_misconception"]

            err_type, mis_id, conf, exp = MisconceptionDNAEngine.classify_error(
                model_prediction=proposed_mis,
                model_confidence=model_conf_estimate,
                submitted_answer=student_answer,
                reasoning_text=student_reasoning or "",
                solved_recently=False,
                repeat_error_count=learner_state.attempts_on_item - 1,
            )
            detected_misconception_id = mis_id
            misconception_conf = conf

            # Record active misconception
            if mis_id and mis_id not in learner_state.active_misconceptions:
                learner_state.active_misconceptions.append(mis_id)

        # 4. Adaptive Teaching Engine strategy selection
        proposed_strat = "progressive_hint"
        if raw_model_proposal and raw_model_proposal.get("selected_strategy"):
            proposed_strat = raw_model_proposal["selected_strategy"]

        selected_strategy, rationale, hint_level = AdaptiveTeachingEngine.select_strategy(
            learner_state=learner_state,
            proposed_strategy=proposed_strat,
            is_over_general_rule=True if detected_misconception_id else False,
        )

        # 5. Build progressive hint (leakage protected)
        hint_text = None
        if not is_correct:
            hint_text = AdaptiveTeachingEngine.build_progressive_hint(
                concept_id=concept_id,
                hint_level=hint_level,
                hint_ladder=hint_ladder,
                expected_answer=canonical_answer,
            )

        # 6. TransferProof check trigger if student is correct
        next_question = None
        mastery_evidence = None
        if is_correct:
            tp_data = TransferProofGenerator.generate_transfer_item(
                concept_id=concept_id,
                seen_question_ids=[],
                transfer_level="medium",
            )
            next_question = tp_data["question"]

            # Record mastery evidence
            mastery_evidence = TransferProofGenerator.record_transfer_evidence(
                item_id=next_question.id,
                transfer_level="medium",
                is_correct=True,
                hints_used=learner_state.hint_level_used,
            )

        # 7. Record turn in session manager
        self.session_manager.log_turn(
            session_id=session_id,
            student_message=student_answer,
            student_reasoning=student_reasoning,
            chosen_strategy=selected_strategy,
            intervention_text=hint_text or "Correct! Transfer item scheduled.",
            detected_misconception=detected_misconception_id,
            answer_revealed=False,
        )

        # 8. Construct validated ModelResponseSchema
        return ModelResponseSchema(
            concept=concept_id,
            learner_state=learner_state,
            detected_misconception=detected_misconception_id,
            misconception_confidence=misconception_conf,
            selected_strategy=selected_strategy,
            explanation=rationale,
            hint=hint_text,
            next_question=next_question,
            expected_answer=None, # Guard: withhold expected answer from student response
            visualization_spec=None,
            answer_revealed=False,
            mastery_evidence=mastery_evidence,
        )
