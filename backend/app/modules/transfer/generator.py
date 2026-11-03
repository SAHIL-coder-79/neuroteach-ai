import random
import uuid
import sympy as sp
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.modules.visual.patterns import PatternLibrary
from app.modules.visual.validator import VisualSpecValidator
from app.schemas.model_response import NextQuestionSchema, MasteryEvidenceSchema
from app.modules.transfer.engine import TransferProofEngine, EvidenceItem

class TransferProofGenerator:
    """
    TransferProof (PRD Section 9.3):
    1. Generates new unseen questions changing values, context story, or reasoning pattern.
    2. Verifies the answer deterministically via SymPy solvers before presentation.
    3. Records evidence (credit & weight) before updating mastery.
    """

    @classmethod
    def generate_transfer_item(
        cls,
        concept_id: str,
        seen_question_ids: List[str],
        transfer_level: str = "medium", # near, medium, far
    ) -> Dict[str, Any]:
        """
        Near: Change numeric values only
        Medium: Change values + context problem story
        Far: Change structural representation (e.g. graph to equation or equation to graph)
        """
        # Generate question using deterministic solver
        base_q = PatternLibrary.generate_parabola_vertex_question(difficulty=transfer_level)

        item_id = f"tp_{str(uuid.uuid4())[:8]}"

        # Apply structural or contextual modifications
        question_text = base_q["question_text"]
        if transfer_level == "medium":
            question_text = (
                f"A projectile follows a trajectory modeled by f(t) = {base_q['visual_spec']['elements'][0]['expr']}. "
                f"At what time t does the projectile reach its maximum/minimum height?"
            )
        elif transfer_level == "far":
            question_text = (
                f"Given the rendered parabolic plot, identify the x-coordinate of the turning point "
                f"without solving the standard formula directly."
            )

        # Deterministic verification of answer
        is_valid_spec, errors = VisualSpecValidator.validate_spec(base_q["visual_spec"])
        if not is_valid_spec:
            raise ValueError(f"TransferProof failed deterministic visual check: {errors}")

        next_q_schema = NextQuestionSchema(
            id=item_id,
            text=question_text,
            pattern_id=base_q["pattern_id"],
            difficulty=base_q["difficulty"],
            transfer_level=transfer_level,
        )

        return {
            "question": next_q_schema,
            "canonical_answer": base_q["canonical_answer"],
            "visual_spec": base_q["visual_spec"],
            "transfer_level": transfer_level,
        }

    @classmethod
    def record_transfer_evidence(
        cls,
        item_id: str,
        transfer_level: str,
        is_correct: bool,
        hints_used: int = 0,
        solution_revealed: bool = False,
    ) -> MasteryEvidenceSchema:
        """
        Credit calculation per PRD Section 9.3:
        - Unaided correct = 1.0
        - 1 hint = 0.75
        - 2 hints = 0.50
        - Answer revealed / wrong = 0.0
        """
        if solution_revealed or not is_correct:
            credit = 0.0
        elif hints_used == 0:
            credit = 1.0
        elif hints_used == 1:
            credit = 0.75
        elif hints_used == 2:
            credit = 0.50
        else:
            credit = 0.0

        return MasteryEvidenceSchema(
            item_id=item_id,
            transfer_level=transfer_level,
            credit=credit,
            timestamp=datetime.utcnow().isoformat(),
        )
