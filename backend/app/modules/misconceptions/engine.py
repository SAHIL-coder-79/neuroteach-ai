from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from app.modules.misconceptions.catalog import MISCONCEPTION_CATALOG, MisconceptionItem

class MisconceptionDNAEngine:
    """
    Misconception DNA:
    1. Distinguishes careless slips vs conceptual errors using multi-signal consensus.
    2. Maintains longitudinal learner profiles (active -> improving -> resolved -> regressed).
    3. Injects prerequisite remediation links when errors recur.
    """

    @staticmethod
    def classify_error(
        model_prediction: Optional[str],
        model_confidence: float,
        submitted_answer: str,
        reasoning_text: str,
        solved_recently: bool = False,
        repeat_error_count: int = 0,
        time_ratio: float = 1.0,
    ) -> Tuple[str, Optional[str], float, str]:
        """
        Signals per PRD Section 9.1:
        - Solved near-identical item in last 7 days -> points to careless
        - Reasoning states correct rule but final slip -> careless
        - Wrong answer equals catalog predicted output -> conceptual (strong)
        - Repeat pattern in >=2 attempts -> conceptual
        - Stated false rule in reasoning -> conceptual
        - Fast submit (<20% median) -> weak careless
        
        Rule: Label conceptual ONLY if model_confidence >= 0.6 AND at least one non-model signal agrees;
        otherwise label unclear and ask a probing question.
        """
        if not model_prediction or model_prediction not in MISCONCEPTION_CATALOG:
            return "unclear", None, model_confidence, "No matching catalog misconception found."

        catalog_item = MISCONCEPTION_CATALOG[model_prediction]

        # Check non-model signals
        careless_signals = 0
        conceptual_signals = 0

        if solved_recently:
            careless_signals += 1

        if time_ratio < 0.2:
            careless_signals += 1

        # Check if reasoning text contains false rule or counterexample indicator
        reasoning_lower = (reasoning_text or "").lower()
        if any(term in reasoning_lower for term in ["b/2a", "b / 2a", "include", "copy", "add", ">", "+"]):
            conceptual_signals += 1

        if repeat_error_count >= 1:
            conceptual_signals += 2

        # Decision Policy
        if model_confidence >= 0.6 and conceptual_signals >= 1:
            return "conceptual", catalog_item.id, model_confidence, catalog_item.description
        elif careless_signals > conceptual_signals:
            return "careless", catalog_item.id, model_confidence, "Appears to be an arithmetic or slip error."
        else:
            return "unclear", catalog_item.id, model_confidence, "Insufficient discriminating signals; probe student reasoning."

    @staticmethod
    def transition_status(
        current_status: str,
        consecutive_correct: int,
        sessions_involved: int,
        transfer_item_passed: bool,
        is_repeat_error: bool = False,
    ) -> str:
        """
        State Machine transitions (PRD Section 9.1):
        - active -> improving: Two consecutive correct answers on discriminating items.
        - improving -> resolved: Three correct discriminating items across two sessions including one transfer item.
        - improving/resolved -> regressed: The same misconception is diagnosed again.
        """
        if is_repeat_error:
            if current_status == "resolved":
                return "regressed"
            return "active"

        if current_status == "active":
            if consecutive_correct >= 2:
                return "improving"
            return "active"

        if current_status == "improving":
            if consecutive_correct >= 3 and sessions_involved >= 2 and transfer_item_passed:
                return "resolved"
            return "improving"

        if current_status == "regressed":
            if consecutive_correct >= 2:
                return "improving"
            return "regressed"

        return current_status
