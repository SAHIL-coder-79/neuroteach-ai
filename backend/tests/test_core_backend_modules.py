import pytest
from app.modules.learner.manager import LearnerStateManager
from app.modules.session.manager import TeachingSessionManager
from app.modules.policy.adaptive_engine import AdaptiveTeachingEngine
from app.modules.transfer.generator import TransferProofGenerator
from app.modules.tutor.orchestrator import PedagogicalCoreOrchestrator
from app.schemas.model_response import ModelResponseSchema

def test_learner_state_management():
    mgr = LearnerStateManager()
    state = mgr.get_or_create_state("student_1", "quadratic.vertex")
    assert state.student_id == "student_1"
    assert state.attempts_on_item == 0

    # Wrong attempt increases attempts count
    s2 = mgr.record_attempt("student_1", "quadratic.vertex", is_correct=False)
    assert s2.attempts_on_item == 1
    assert s2.consecutive_correct_steps == 0

    # Correct attempt fades assistance
    s2.hint_level_used = 2
    s3 = mgr.record_attempt("student_1", "quadratic.vertex", is_correct=True)
    assert s3.consecutive_correct_steps == 1
    assert s3.hint_level_used == 1 # Reduced assistance (support fading)

def test_session_management():
    sess_mgr = TeachingSessionManager()
    session = sess_mgr.create_session("student_1", "mathematics", "quadratic.vertex")
    assert session.is_active is True
    assert len(session.turns) == 0

    turn = sess_mgr.log_turn(
        session_id=session.session_id,
        student_message="-2",
        student_reasoning="Used x=b/2a",
        chosen_strategy="counterexample",
        intervention_text="Consider what happens when b is negative.",
        detected_misconception="sign_error_vertex",
    )
    assert turn.turn_index == 1
    assert len(session.turns) == 1

def test_adaptive_teaching_engine_failure_pivot():
    mgr = LearnerStateManager()
    state = mgr.get_or_create_state("student_2", "quadratic.vertex")

    # Record 2 consecutive failures on progressive_hint
    mgr.record_strategy_outcome("student_2", "quadratic.vertex", "progressive_hint", "fail")
    mgr.record_strategy_outcome("student_2", "quadratic.vertex", "progressive_hint", "fail")

    strat, rationale, hint_level = AdaptiveTeachingEngine.select_strategy(
        learner_state=state,
        proposed_strategy="progressive_hint",
        is_over_general_rule=True
    )
    # Must switch away from progressive_hint
    assert strat != "progressive_hint"
    assert "failed 2 times" in rationale

def test_adaptive_teaching_engine_answer_leakage_protection():
    ladder = [
        "Recall the formula for axis of symmetry.",
        "The answer is 2, just write that down.", # Malformed leaking hint
        "Use x = -b / (2a) with signs."
    ]
    safe_hint = AdaptiveTeachingEngine.build_progressive_hint(
        concept_id="quadratic.vertex",
        hint_level=2,
        hint_ladder=ladder,
        expected_answer="2"
    )
    # Leaking string should be dropped and sanitized
    assert "the answer is 2" not in safe_hint.lower()

def test_transferproof_item_generation_and_evidence():
    tp = TransferProofGenerator.generate_transfer_item("quadratic.vertex", [], transfer_level="medium")
    assert tp["question"].id.startswith("tp_")
    assert tp["transfer_level"] == "medium"
    assert "visual_spec" in tp

    evidence = TransferProofGenerator.record_transfer_evidence(
        item_id=tp["question"].id,
        transfer_level="medium",
        is_correct=True,
        hints_used=1
    )
    assert evidence.credit == 0.75 # 1 hint credit = 0.75

def test_pedagogical_core_orchestrator_schema_compliance():
    orch = PedagogicalCoreOrchestrator()
    session = orch.session_manager.create_session("student_3", "mathematics", "quadratic.vertex")

    ladder = [
        "Level 1: Recall the standard axis of symmetry formula.",
        "Level 2: Here a = 1 and b = -4.",
        "Level 3: Substitute values into x = -(-4) / (2 * 1)."
    ]

    response = orch.process_student_turn(
        session_id=session.session_id,
        student_id="student_3",
        concept_id="quadratic.vertex",
        student_answer="-2",
        student_reasoning="Used x = b / 2a",
        canonical_answer="2",
        hint_ladder=ladder,
    )

    # Validate strict Pydantic model response compliance
    assert isinstance(response, ModelResponseSchema)
    assert response.concept == "quadratic.vertex"
    assert response.detected_misconception == "sign_error_vertex"
    assert response.misconception_confidence >= 0.6
    assert response.selected_strategy in ["progressive_hint", "counterexample"]
    assert response.hint is not None
    assert response.answer_revealed is False
