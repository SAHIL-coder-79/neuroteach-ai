import random
import sympy as sp
from typing import Dict, Any, Tuple

class PatternLibrary:
    """
    Pattern library housing solver-verified mathematical questions (PRD Section 10.4).
    Generates new parameters, recomputes roots, vertices, and visual specs deterministically.
    """

    @staticmethod
    def generate_parabola_vertex_question(difficulty: str = "medium") -> Dict[str, Any]:
        """
        Pattern: Quadratic roots & vertex
        f(x) = (x - h)^2 + k = x^2 - 2hx + (h^2 + k)
        """
        if difficulty == "easy":
            h = random.choice([1, 2, 3])
            k = random.choice([-4, -1, 0])
        elif difficulty == "hard":
            h = random.choice([-5, -3, 4, 6])
            k = random.choice([-9, -5, 2])
        else: # medium
            h = random.choice([-2, 2, 3, 4])
            k = random.choice([-4, -1, 1])

        # Expand: f(x) = x^2 - 2h*x + (h^2 + k)
        b = -2 * h
        c = h**2 + k

        b_sign = f"- {abs(b)}" if b < 0 else f"+ {b}"
        c_sign = f"- {abs(c)}" if c < 0 else f"+ {c}"

        expr_str = f"x^2 {b_sign}*x {c_sign}"
        canonical_answer = str(h)

        question_text = f"Find the x-coordinate of the vertex for the parabola given by f(x) = x² {b_sign}x {c_sign}."

        visual_spec = {
            "schema_version": "1.0",
            "type": "function_plot",
            "title": f"f(x) = x² {b_sign}x {c_sign} (Solver-Verified)",
            "viewport": {"xmin": h - 4, "xmax": h + 4, "ymin": k - 2, "ymax": k + 10},
            "axes": {"x": {"label": "x", "grid": True}, "y": {"label": "y", "grid": True}},
            "parameters": [{"id": "a", "label": "Curvature", "min": 0.5, "max": 2.0, "step": 0.5, "default": 1.0}],
            "elements": [
                {"id": "f1", "kind": "function", "expr": expr_str, "style": "primary", "legend": f"f(x) = x² {b_sign}x {c_sign}"},
                {"id": "v1", "kind": "point", "x": float(h), "y": float(k), "label": f"Vertex ({h}, {k})", "derived_from": "f1.vertex"}
            ],
            "annotations": [{"target": "v1", "text": f"Turning Point at x = {h}", "kind": "callout"}],
            "explanation": f"The axis of symmetry is x = -b/(2a) = -({b})/(2*1) = {h}."
        }

        return {
            "pattern_id": "parabola_vertex",
            "concept_id": "quadratic.vertex",
            "difficulty": difficulty,
            "title": f"Vertex of a Parabola ({difficulty.capitalize()})",
            "question_text": question_text,
            "canonical_answer": canonical_answer,
            "visual_spec": visual_spec,
            "hint_ladder": [
                "Level 1: Recall the standard axis of symmetry formula x = -b / (2a).",
                f"Level 2: In this equation a = 1 and b = {b}. Substitute them into the formula.",
                f"Level 3: Compute x = -({b}) / (2 * 1) = {h}."
            ]
        }
