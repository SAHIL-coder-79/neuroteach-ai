from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EvidenceItem(BaseModel):
    item_id: str
    transfer_level: str # near (0.5), medium (0.8), far (1.0)
    credit: float # 0.0 - 1.0 (unaided=1.0, 1 hint=0.75, 2 hints=0.5, revealed/wrong=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TransferProofEngine:
    """
    TransferProof (PRD Section 9.3):
    - Refuses to declare mastery from a single correct answer.
    - Evaluates Near, Medium, and Far transfer checks.
    - Computes Bayesian smoothed mastery:
      M = (alpha_0 + sum(w_i * c_i)) / (alpha_0 + beta_0 + sum(w_i))
      where alpha_0 = 1, beta_0 = 1.
    """

    ALPHA_0 = 1.0
    BETA_0 = 1.0

    LEVEL_WEIGHTS = {
        "near": 0.5,
        "medium": 0.8,
        "far": 1.0,
    }

    @classmethod
    def compute_mastery(
        cls,
        evidence_items: List[EvidenceItem],
        active_misconceptions_count: int = 0,
        unique_sessions_count: int = 1,
    ) -> Dict[str, Any]:
        """
        Computes Bayesian smoothed mastery score and evaluates master condition.
        Mastered requires:
        - M >= 0.80
        - >= 3 unassisted or 1-hint transfer items (credit >= 0.75)
        - >= 1 medium or far transfer item
        - Evidence across >= 2 sessions
        - 0 active misconceptions
        """
        if not evidence_items:
            # Baseline prior: 1 / (1 + 1) = 0.5 smoothed or 0 if unattempted
            raw_m = cls.ALPHA_0 / (cls.ALPHA_0 + cls.BETA_0)
            return {
                "mastery_score": 0.0,
                "is_mastered": False,
                "evidence_count": 0,
                "explanation": "No evidence items recorded yet.",
                "missing_conditions": ["At least 3 transfer checks", "Evidence across >= 2 sessions", "Score >= 0.80"],
            }

        weighted_credit_sum = 0.0
        weight_sum = 0.0
        qualifying_items = 0
        has_medium_or_far = False

        now = datetime.utcnow()

        for item in evidence_items:
            base_weight = cls.LEVEL_WEIGHTS.get(item.transfer_level.lower(), 0.5)
            # Recency factor: 0.9 per 14 days of age
            days_old = (now - item.created_at).days if item.created_at else 0
            recency_factor = 0.9 ** (max(0, days_old) / 14.0)
            w = base_weight * recency_factor

            c = max(0.0, min(1.0, item.credit))
            weighted_credit_sum += w * c
            weight_sum += w

            if item.credit >= 0.75:
                qualifying_items += 1
            if item.transfer_level.lower() in ["medium", "far"] and item.credit >= 0.5:
                has_medium_or_far = True

        mastery_score = (cls.ALPHA_0 + weighted_credit_sum) / (cls.ALPHA_0 + cls.BETA_0 + weight_sum)
        mastery_score = round(mastery_score, 4)

        # Check all required conditions
        missing = []
        if mastery_score < 0.80:
            missing.append(f"Score {mastery_score:.2f} is below 0.80 threshold")
        if qualifying_items < 3:
            missing.append(f"Only {qualifying_items}/3 qualifying transfer checks passed")
        if not has_medium_or_far:
            missing.append("Requires at least 1 Medium or Far transfer item")
        if unique_sessions_count < 2:
            missing.append("Requires evidence distributed across at least 2 distinct sessions")
        if active_misconceptions_count > 0:
            missing.append(f"Contains {active_misconceptions_count} active catalog misconceptions")

        is_mastered = len(missing) == 0

        return {
            "mastery_score": mastery_score,
            "is_mastered": is_mastered,
            "evidence_count": len(evidence_items),
            "qualifying_items": qualifying_items,
            "has_medium_or_far": has_medium_or_far,
            "missing_conditions": missing,
            "explanation": "Mastery confirmed across multi-context transfer items." if is_mastered else "; ".join(missing),
        }
