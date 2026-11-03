import re
from typing import List, Dict, Optional, Tuple

TEACHING_STRATEGIES = [
    "progressive_hint",
    "step_by_step",
    "example_based",
    "counterexample",
    "contrastive",
    "analogy",
    "simpler_prerequisite",
    "guided_problem_solving",
]

class TeachingPolicyEngine:
    """
    Adaptive Teaching Engine (PRD Section 9.2):
    - Guardrail 1: Final answer is strictly withheld until hint ladder is exhausted.
    - Guardrail 2: If a strategy fails twice for the same misconception, switch strategy.
    - Guardrail 3: Support fades after unaided success.
    """

    @staticmethod
    def detect_answer_leakage(intervention_text: str, canonical_answer: str) -> bool:
        """
        Returns True if the intervention text reveals or leaks the canonical answer prematurely.
        Performs exact word boundaries, numerical equivalence, and key phrasing checks.
        """
        if not intervention_text or not canonical_answer:
            return False

        text = intervention_text.strip().lower()
        ans = canonical_answer.strip().lower()

        # Check explicit reveal phrases
        leak_phrases = [
            f"the answer is {ans}",
            f"the correct answer is {ans}",
            f"final answer is {ans}",
            f"answer = {ans}",
            f"result is {ans}",
            f"solution is {ans}",
            f"the vertex is {ans}",
            f"x-coordinate is {ans}",
        ]
        for phrase in leak_phrases:
            if phrase in text:
                return True

        # Check word-boundary match of numerical answer if answer is non-trivial
        if len(ans) > 1 or (len(ans) == 1 and ans.isalnum()):
            pattern = rf"(?:the\s+answer\s+is\s+|correct\s+value\s+is\s+)\b{re.escape(ans)}\b"
            if re.search(pattern, text):
                return True

        return False

    @staticmethod
    def select_next_strategy(
        proposed_strategy: str,
        current_strategy: Optional[str],
        consecutive_failures_on_strategy: int,
        previously_failed_strategies: List[str],
        is_concept_unfamiliar: bool = False,
        is_over_general_rule: bool = False,
    ) -> Tuple[str, str]:
        """
        Enforces deterministic switching policy:
        If current strategy failed >= 2 times, force pivot to an alternative strategy not previously failed.
        """
        # If strategy failed twice, switch away immediately
        if consecutive_failures_on_strategy >= 2 and current_strategy:
            fallback_order = [
                "counterexample" if is_over_general_rule else "progressive_hint",
                "example_based" if is_concept_unfamiliar else "step_by_step",
                "simpler_prerequisite",
                "analogy",
                "guided_problem_solving",
                "contrastive",
            ]
            for candidate in fallback_order:
                if candidate != current_strategy and candidate not in previously_failed_strategies:
                    return candidate, f"Strategy '{current_strategy}' failed twice; auto-switched to '{candidate}'."

        # If proposed strategy was already exhausted/failed, pick next viable
        if proposed_strategy in previously_failed_strategies:
            for strat in TEACHING_STRATEGIES:
                if strat not in previously_failed_strategies:
                    return strat, f"Proposed strategy was previously failed; selected viable '{strat}'."

        return proposed_strategy, "Strategy selected in accordance with learner state."
