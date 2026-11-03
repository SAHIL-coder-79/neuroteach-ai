from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class MisconceptionItem(BaseModel):
    id: str
    subject: str
    concept_id: str
    name: str
    description: str
    wrong_rule: str
    counterexample: str
    root_concepts: List[str] = Field(default_factory=list)
    look_alike_slips: List[str] = Field(default_factory=list)

# Curated catalog across Mathematics, Python, DSA, AI/ML (PRD Section 9.1 & 16.3)
MISCONCEPTION_CATALOG: Dict[str, MisconceptionItem] = {
    # Mathematics
    "sign_error_vertex": MisconceptionItem(
        id="sign_error_vertex",
        subject="mathematics",
        concept_id="quadratic.vertex",
        name="Sign Inversion in Axis of Symmetry",
        description="Student computes vertex using x = b/(2a) instead of x = -b/(2a).",
        wrong_rule="x = b / (2 * a)",
        counterexample="For f(x) = x² - 4x + 3, the vertex is at x = +2, but b/(2a) gives -2.",
        root_concepts=["quadratic.standard_form", "algebra.negatives"],
        look_alike_slips=["sign flip in final arithmetic"]
    ),
    "root_product_zero": MisconceptionItem(
        id="root_product_zero",
        subject="mathematics",
        concept_id="quadratic.roots",
        name="Non-Zero Product Property Misapplication",
        description="Assuming (x - a)(x - b) = k implies x - a = k or x - b = k when k != 0.",
        wrong_rule="If (x-a)(x-b) = c, then x-a = c or x-b = c",
        counterexample="(x-1)(x-2) = 6 does not mean x-1 = 6 (x=7 gives 6*5=30 != 6).",
        root_concepts=["algebra.zero_product_property"],
        look_alike_slips=["arithmetic factoring mistake"]
    ),
    "exponent_distribution": MisconceptionItem(
        id="exponent_distribution",
        subject="mathematics",
        concept_id="algebra.powers",
        name="Freshman's Dream Exponent Distribution",
        description="Expanding (a + b)^2 as a^2 + b^2, omitting cross terms.",
        wrong_rule="(a + b)^2 = a^2 + b^2",
        counterexample="(1 + 2)^2 = 9, but 1^2 + 2^2 = 5.",
        root_concepts=["algebra.polynomial_multiplication"],
        look_alike_slips=["forgot middle term during fast expansion"]
    ),
    "slope_reciprocal": MisconceptionItem(
        id="slope_reciprocal",
        subject="mathematics",
        concept_id="linear.slope",
        name="Perpendicular Slope Sign Neglect",
        description="Thinking perpendicular slope is 1/m instead of -1/m.",
        wrong_rule="m_perp = 1 / m",
        counterexample="A line sloping up at m=2 needs a line sloping down (negative) to be perpendicular.",
        root_concepts=["coordinate.geometry.slopes"],
        look_alike_slips=["arithmetic inverse error"]
    ),

    # Python
    "inclusive_range_stop": MisconceptionItem(
        id="inclusive_range_stop",
        subject="python",
        concept_id="python.loops",
        name="Inclusive Range Boundary Assumption",
        description="Assuming range(start, stop) includes stop as the final iteration value.",
        wrong_rule="range(start, stop) generates numbers up to and including stop.",
        counterexample="list(range(1, 4)) produces [1, 2, 3], which has length 3, not 4.",
        root_concepts=["python.indexing.zero_based"],
        look_alike_slips=["typing range(1, 5) when intending 4 iterations"]
    ),
    "mutable_default_argument": MisconceptionItem(
        id="mutable_default_argument",
        subject="python",
        concept_id="python.functions",
        name="Mutable Default Argument Fresh Allocation",
        description="Assuming def f(x=[]): allocates a fresh empty list on every call.",
        wrong_rule="Default parameters are evaluated each time the function is invoked.",
        counterexample="Appending to default list in consecutive calls keeps previous elements.",
        root_concepts=["python.memory.references"],
        look_alike_slips=["omitting x = None check"]
    ),
    "shallow_copy_nested": MisconceptionItem(
        id="shallow_copy_nested",
        subject="python",
        concept_id="python.data_structures",
        name="Shallow Copy Isolates Nested Structures",
        description="Believing list.copy() or [:] clones nested inner lists.",
        wrong_rule="list.copy() creates a fully independent deep duplicate of all contents.",
        counterexample="Modifying a[0].append(1) in a shallow copy alters the original list.",
        root_concepts=["python.memory.pointers"],
        look_alike_slips=["using copy instead of deepcopy by typo"]
    ),

    # DSA
    "bst_left_larger": MisconceptionItem(
        id="bst_left_larger",
        subject="dsa",
        concept_id="dsa.bst",
        name="BST Ordering Inversion",
        description="Inserting elements larger than root into left subtree.",
        wrong_rule="left_child > root",
        counterexample="In a valid BST, all elements in left subtree must be strictly less than root.",
        root_concepts=["dsa.binary_tree_properties"],
        look_alike_slips=["accidental comparator swap in code"]
    ),
    "binary_search_boundary": MisconceptionItem(
        id="binary_search_boundary",
        subject="dsa",
        concept_id="dsa.binary_search",
        name="Binary Search Range Truncation (low = mid)",
        description="Setting low = mid or high = mid causing infinite loops on size 2 arrays.",
        wrong_rule="low = mid when target > arr[mid]",
        counterexample="When low=0, high=1, mid=0; if arr[mid] < target, setting low=mid repeats mid=0 forever.",
        root_concepts=["dsa.loop_invariants"],
        look_alike_slips=["off-by-one pointer slip"]
    ),
    "heap_sorted_levels": MisconceptionItem(
        id="heap_sorted_levels",
        subject="dsa",
        concept_id="dsa.heap",
        name="Heap Level Total Ordering",
        description="Assuming items in min-heap level k are always smaller than level k+1 globally.",
        wrong_rule="All nodes at depth d are smaller than all nodes at depth d+1.",
        counterexample="A node on the right side of level 2 can be larger than a node on left of level 3.",
        root_concepts=["dsa.partial_orders"],
        look_alike_slips=["confusing heap with BST"]
    ),

    # AI / ML
    "gradient_descent_sign": MisconceptionItem(
        id="gradient_descent_sign",
        subject="ai_ml",
        concept_id="aiml.optimization",
        name="Gradient Ascent Sign Confusion",
        description="Adding learning_rate * gradient instead of subtracting when minimizing loss.",
        wrong_rule="w_new = w + lr * gradient",
        counterexample="The gradient points towards steepest ascent; adding it increases loss instead of minimizing.",
        root_concepts=["calculus.gradients", "optimization.loss_surfaces"],
        look_alike_slips=["typo in minus sign"]
    ),
    "r2_score_bounded_zero": MisconceptionItem(
        id="r2_score_bounded_zero",
        subject="ai_ml",
        concept_id="aiml.regression",
        name="R-Squared Lower Bound Fallacy",
        description="Believing R² score is always bounded between 0 and 1.",
        wrong_rule="R² can never be negative.",
        counterexample="A model that predicts worse than the horizontal mean line has R² < 0.",
        root_concepts=["statistics.variance_decomposition"],
        look_alike_slips=["confusing R² with r² (Pearson correlation squared)"]
    ),
}

def get_catalog_misconception(misconception_id: str) -> Optional[MisconceptionItem]:
    return MISCONCEPTION_CATALOG.get(misconception_id)
