import pytest
from app.modules.policy.engine import TeachingPolicyEngine
from app.modules.misconceptions.engine import MisconceptionDNAEngine
from app.modules.transfer.engine import TransferProofEngine, EvidenceItem
from app.modules.visual.validator import VisualSpecValidator
from app.modules.visual.patterns import PatternLibrary

def test_leakage_detector():
    # Direct leak should be caught
    assert TeachingPolicyEngine.detect_answer_leakage("The answer is 2.", "2") is True
    assert TeachingPolicyEngine.detect_answer_leakage("So the vertex is 2", "2") is True
    # Non-leaking hint should pass
    assert TeachingPolicyEngine.detect_answer_leakage("Remember to check the minus sign in -b/(2a).", "2") is False

def test_policy_strategy_switch_after_failures():
    strat, reason = TeachingPolicyEngine.select_next_strategy(
        proposed_strategy="progressive_hint",
        current_strategy="progressive_hint",
        consecutive_failures_on_strategy=2,
        previously_failed_strategies=["progressive_hint"],
        is_over_general_rule=True
    )
    assert strat != "progressive_hint"
    assert "auto-switched" in reason

def test_misconception_classification():
    err_type, mis_id, conf, exp = MisconceptionDNAEngine.classify_error(
        model_prediction="sign_error_vertex",
        model_confidence=0.85,
        submitted_answer="-2",
        reasoning_text="I used x = b / 2a",
        repeat_error_count=1
    )
    assert err_type == "conceptual"
    assert mis_id == "sign_error_vertex"

def test_transferproof_bayesian_mastery():
    # 4 high-credit transfer items (near, medium, far, far)
    items = [
        EvidenceItem(item_id="i1", transfer_level="near", credit=1.0),
        EvidenceItem(item_id="i2", transfer_level="medium", credit=1.0),
        EvidenceItem(item_id="i3", transfer_level="far", credit=1.0),
        EvidenceItem(item_id="i4", transfer_level="far", credit=1.0),
        EvidenceItem(item_id="i5", transfer_level="medium", credit=1.0),
    ]
    res = TransferProofEngine.compute_mastery(
        evidence_items=items,
        active_misconceptions_count=0,
        unique_sessions_count=2
    )
    assert res["mastery_score"] >= 0.80
    assert res["is_mastered"] is True

def test_visual_spec_validator_rejection():
    # Corrupted spec with wrong vertex should be rejected
    bad_spec = {
        "type": "function_plot",
        "elements": [
            {"id": "f1", "kind": "function", "expr": "x^2 - 4*x + 3"},
            {"id": "v1", "kind": "point", "x": 99.0, "y": 0.0, "derived_from": "f1.vertex"}
        ]
    }
    is_valid, errors = VisualSpecValidator.validate_spec(bad_spec)
    print("DEBUG ERRORS:", errors)
    assert is_valid is False
    assert any("vertex" in err.lower() for err in errors)

def test_pattern_library_generation():
    q = PatternLibrary.generate_parabola_vertex_question(difficulty="easy")
    assert "question_text" in q
    assert "visual_spec" in q
    is_valid, errs = VisualSpecValidator.validate_spec(q["visual_spec"])
    if not is_valid:
        print("PATTERN ERRORS:", errs)
    assert is_valid is True
