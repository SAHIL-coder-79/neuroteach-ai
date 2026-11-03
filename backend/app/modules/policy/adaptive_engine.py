import re
from typing import List, Dict, Any, Optional, Tuple
from app.schemas.model_response import LearnerStateSchema, StrategyRecord

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

class AdaptiveTeachingEngine:
    """
    Adaptive Teaching Engine (PRD Section 9.2):
    - Selects teaching strategies based on learner state.
    - Tracks previous strategies and outcomes.
    - Avoids repeating an unsuccessful strategy without a reason (switches after 2 fails).
    - Prevents immediate answer reveals.
    - Delivers progressively more helpful hints (Level 1 -> 2 -> 3).
    - Reduces assistance when understanding improves (support fading).
    """

    @staticmethod
    def detect_answer_leakage(intervention_text: str, expected_answer: Optional[str]) -> bool:
        if not intervention_text or not expected_answer:
            return False

        text = intervention_text.strip().lower()
        ans = expected_answer.strip().lower()

        leak_phrases = [
            f"the answer is {ans}",
            f"the correct answer is {ans}",
            f"equals {ans}",
            f"= {ans}",
            f"result is {ans}",
            f"giving {ans}",
            f"final answer is {ans}",
            f"vertex is {ans}",
            f"x = {ans}",
        ]
        for phrase in leak_phrases:
            if phrase in text:
                return True

        if len(ans) > 1 or (len(ans) == 1 and ans.isalnum()):
            pattern = rf"(?:the\s+answer\s+is\s+|correct\s+value\s+is\s+)\b{re.escape(ans)}\b"
            if re.search(pattern, text):
                return True

        return False

    @staticmethod
    def select_strategy(
        learner_state: LearnerStateSchema,
        proposed_strategy: str = "progressive_hint",
        is_concept_unfamiliar: bool = False,
        is_over_general_rule: bool = False,
    ) -> Tuple[str, str, int]:
        """
        Selects or validates strategy based on history and state:
        - Returns (strategy_name, rationale, hint_level)
        """
        recent_strategies = learner_state.strategies_tried
        current_streak_failures = 0
        last_strategy_name = None

        if recent_strategies:
            last_strategy_name = recent_strategies[-1].name
            # Count consecutive failures on the last strategy
            for rec in reversed(recent_strategies):
                if rec.name == last_strategy_name and rec.outcome == "fail":
                    current_streak_failures += 1
                else:
                    break

        # Rule: Avoid repeating an unsuccessful strategy after 2 failures
        if current_streak_failures >= 2 and last_strategy_name:
            failed_set = {r.name for r in recent_strategies if r.outcome == "fail"}
            fallback_order = [
                "counterexample" if is_over_general_rule else "progressive_hint",
                "example_based" if is_concept_unfamiliar else "step_by_step",
                "simpler_prerequisite",
                "analogy",
                "guided_problem_solving",
                "contrastive",
            ]
            for cand in fallback_order:
                if cand != last_strategy_name and cand not in failed_set:
                    return (
                        cand,
                        f"Strategy '{last_strategy_name}' failed {current_streak_failures} times; auto-switched to '{cand}'.",
                        1,
                    )

        # Fading assistance: If consecutive correct steps > 0, decrease hint level
        if learner_state.consecutive_correct_steps > 0:
            effective_level = max(1, learner_state.hint_level_used)
            return (
                proposed_strategy,
                "Learner showed improvement; reducing scaffolding (support fading).",
                effective_level,
            )

        # Progressive hints: increase assistance up to level 3
        hint_level = min(3, learner_state.hint_level_used + 1)
        return (
            proposed_strategy,
            f"Progressing assistance to hint level {hint_level}.",
            hint_level,
        )

    @staticmethod
    def build_progressive_hint(
        concept_id: str,
        hint_level: int,
        hint_ladder: List[str],
        expected_answer: Optional[str] = None,
    ) -> str:
        """
        Returns a scaffolded hint corresponding to level (1, 2, or 3).
        Guarantees that the returned hint does not leak the expected answer.
        """
        if not hint_ladder:
            return "Review the definition and steps for this concept."

        idx = max(0, min(len(hint_ladder) - 1, hint_level - 1))
        candidate_hint = hint_ladder[idx]

        # Guard against answer leakage
        if expected_answer and AdaptiveTeachingEngine.detect_answer_leakage(candidate_hint, expected_answer):
            return "Check each sign and parameter step by step without skipping terms."

        return candidate_hint
