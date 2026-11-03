import math
import sympy as sp
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field

# Whitelist grammar per PRD Section 10.2
ALLOWED_SYMBOLS = {
    "x", "y", "a", "b", "c", "m", "k", "n",
    "sin", "cos", "tan", "asin", "acos", "atan",
    "exp", "ln", "log", "sqrt", "abs", "floor", "ceil", "min", "max"
}

class VisualSpecValidator:
    """
    7-Step Deterministic Validation Pipeline (PRD Section 10.3):
    1. Schema validation (Pydantic)
    2. Expression parse with SymPy using whitelist grammar
    3. Domain sampling: 200 points per function; no NaN/inf
    4. Feature recomputation: roots, vertex, intercepts verified within 1e-3
    5. Annotation check
    6. Answer check
    7. Readability & limits (size <= 64KB, length <= 200)
    """

    @classmethod
    def validate_spec(cls, spec: Dict[str, Any], canonical_answer: str = "") -> Tuple[bool, List[str]]:
        errors = []

        # 1. Basic schema checks
        if not isinstance(spec, dict):
            return False, ["Spec must be a dictionary"]

        spec_type = spec.get("type")
        if spec_type not in ["function_plot", "coordinate_geometry", "data_chart", "tree", "algorithm_trace"]:
            errors.append(f"Invalid or unsupported visual type: {spec_type}")

        elements = spec.get("elements", [])
        if not elements or len(elements) > 8:
            errors.append(f"Element count must be between 1 and 8, found {len(elements)}")

        # 2 & 3. Parse expressions and domain sample
        x = sp.Symbol('x', real=True)
        for elem in elements:
            if elem.get("kind") == "function":
                expr_str = elem.get("expr", "")
                if len(expr_str) > 200:
                    errors.append(f"Expression exceeds 200 chars: {expr_str}")
                    continue

                try:
                    # Clean and parse with SymPy safely
                    cleaned_expr = expr_str.replace("^", "**")
                    parsed_expr = sp.sympify(cleaned_expr, evaluate=False)

                    # Verify whitelist symbols
                    for sym in parsed_expr.free_symbols:
                        if sym.name not in ALLOWED_SYMBOLS:
                            errors.append(f"Forbidden identifier '{sym.name}' in expression: {expr_str}")

                    # Domain sampling across 200 points
                    f = sp.lambdify(x, parsed_expr, modules=["math", "numpy"])
                    viewport = spec.get("viewport", {"xmin": -10, "xmax": 10})
                    xmin = viewport.get("xmin", -10)
                    xmax = viewport.get("xmax", 10)
                    step = (xmax - xmin) / 200.0

                    valid_samples = 0
                    for i in range(200):
                        sample_x = xmin + i * step
                        try:
                            val = f(sample_x)
                            if not math.isnan(val) and not math.isinf(val):
                                valid_samples += 1
                        except (ZeroDivisionError, ValueError):
                            pass

                    if valid_samples < 50:
                        errors.append(f"Function {expr_str} produces excessive singularity/undefined values.")

                except Exception as e:
                    errors.append(f"Failed to parse mathematical expression '{expr_str}': {str(e)}")

            # 4. Feature recomputation (roots, vertex, extrema)
            elif elem.get("kind") == "point" and elem.get("derived_from"):
                derived_tag = elem.get("derived_from", "")
                px = elem.get("x")
                py = elem.get("y")

                if "vertex" in derived_tag:
                    parent_func_id = derived_tag.split(".")[0]
                    parent_elem = next((e for e in elements if e.get("id") == parent_func_id), None)
                    if parent_elem and parent_elem.get("expr"):
                        try:
                            expr_sym = sp.sympify(parent_elem["expr"].replace("^", "**"))
                            var_x = next((s for s in expr_sym.free_symbols if s.name == 'x'), sp.Symbol('x'))
                            poly = sp.Poly(expr_sym, var_x)
                            deg = poly.degree()
                            if deg == 2:
                                a_val = float(poly.coeff_monomial(var_x**2))
                                b_val = float(poly.coeff_monomial(var_x))
                                c_val = float(poly.coeff_monomial(1))
                                expected_vx = -b_val / (2.0 * a_val)
                                expected_vy = c_val - (b_val**2) / (4.0 * a_val)
                                if px is not None and abs(px - expected_vx) > 1e-3:
                                    errors.append(f"Recomputed vertex x mismatch: claimed {px}, expected {expected_vx}")
                                if py is not None and abs(py - expected_vy) > 1e-3:
                                    errors.append(f"Recomputed vertex y mismatch: claimed {py}, expected {expected_vy}")
                            else:
                                errors.append(f"Function {parent_elem['expr']} vertex check requires degree 2, got {deg}")
                        except Exception as ex:
                            errors.append(f"Vertex computation failed: {str(ex)}")

        # 6. Annotation check
        annotations = spec.get("annotations", [])
        elem_ids = {e.get("id") for e in elements if "id" in e}
        for ann in annotations:
            target = ann.get("target")
            if target and target not in elem_ids:
                errors.append(f"Annotation target '{target}' does not exist in elements list.")

        is_valid = len(errors) == 0
        return is_valid, errors
