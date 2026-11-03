from typing import Dict, Any, Optional
from datetime import datetime
from app.schemas.model_response import LearnerStateSchema, StrategyRecord

class LearnerStateManager:
    """
    Learner State Management (PRD Section 9.2):
    Tracks mastery snapshots, active misconceptions, recent attempts,
    hint levels, and consecutive unaided steps for support fading.
    """

    def __init__(self):
        self._states: Dict[str, LearnerStateSchema] = {}

    def get_or_create_state(self, student_id: str, concept_id: str) -> LearnerStateSchema:
        key = f"{student_id}:{concept_id}"
        if key not in self._states:
            self._states[key] = LearnerStateSchema(
                student_id=student_id,
                concept_id=concept_id,
                mastery_score=0.0,
                evidence_count=0,
                active_misconceptions=[],
                hint_level_used=0,
                attempts_on_item=0,
                consecutive_correct_steps=0,
                strategies_tried=[],
                recent_accuracy=0.0,
                time_ratio=1.0,
                frustration_flag=False,
            )
        return self._states[key]

    def record_attempt(
        self,
        student_id: str,
        concept_id: str,
        is_correct: bool,
        duration_seconds: float = 30.0,
        median_time: float = 45.0,
    ) -> LearnerStateSchema:
        state = self.get_or_create_state(student_id, concept_id)
        state.attempts_on_item += 1

        if median_time > 0:
            state.time_ratio = duration_seconds / median_time

        if is_correct:
            state.consecutive_correct_steps += 1
            # Rule: After a correct step, reduce assistance level (fade support)
            if state.hint_level_used > 0:
                state.hint_level_used -= 1
            state.recent_accuracy = min(1.0, state.recent_accuracy + 0.2)
            state.frustration_flag = False
        else:
            state.consecutive_correct_steps = 0
            state.recent_accuracy = max(0.0, state.recent_accuracy - 0.2)
            if state.attempts_on_item >= 3:
                state.frustration_flag = True

        return state

    def record_strategy_outcome(
        self,
        student_id: str,
        concept_id: str,
        strategy_name: str,
        outcome: str,
        hint_level: Optional[int] = None,
        rationale: Optional[str] = None,
    ) -> LearnerStateSchema:
        state = self.get_or_create_state(student_id, concept_id)
        state.strategies_tried.append(
            StrategyRecord(
                name=strategy_name,
                outcome=outcome,
                hint_level=hint_level,
                rationale=rationale,
            )
        )
        return state

    def update_misconceptions(
        self,
        student_id: str,
        concept_id: str,
        active_misconceptions: list[str],
    ) -> LearnerStateSchema:
        state = self.get_or_create_state(student_id, concept_id)
        state.active_misconceptions = active_misconceptions
        return state
