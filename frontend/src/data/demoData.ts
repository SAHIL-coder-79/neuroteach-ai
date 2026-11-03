import { ConceptNode, QuestionItem } from '../types';

export const DEMO_NOTICE = "Demonstration data strictly for MVP evaluation and layout verification.";

export const DEMO_CONCEPTS: ConceptNode[] = [
  {
    id: "quad_standard",
    subject: "mathematics",
    title: "Quadratic Equations: Standard Form",
    description: "Structure y = ax² + bx + c and role of coefficients.",
    status: "mastered",
    mastery_score: 0.94,
    prerequisites: [],
    evidence_count: 5,
  },
  {
    id: "quad_vertex",
    subject: "mathematics",
    title: "Parabola Vertex & Axis of Symmetry",
    description: "Determining vertex coordinates (-b/2a) and extremum points.",
    status: "in_progress",
    mastery_score: 0.65,
    prerequisites: ["quad_standard"],
    evidence_count: 3,
  },
  {
    id: "quad_roots",
    subject: "mathematics",
    title: "Roots and Discriminant Analysis",
    description: "Connecting real roots to x-intercepts visually and algebraically.",
    status: "available",
    mastery_score: 0.20,
    prerequisites: ["quad_vertex"],
    evidence_count: 1,
  },
  {
    id: "calc_limits",
    subject: "mathematics",
    title: "Limits & Continuity",
    description: "Behavior of functions approaching critical values.",
    status: "locked",
    mastery_score: 0.0,
    prerequisites: ["quad_roots"],
    evidence_count: 0,
  },
  {
    id: "py_loops",
    subject: "python",
    title: "Iteration & Range Indexing",
    description: "Off-by-one boundary conditions and indexing mechanics.",
    status: "mastered",
    mastery_score: 0.88,
    prerequisites: [],
    evidence_count: 4,
  },
  {
    id: "dsa_bst_insert",
    subject: "dsa",
    title: "Binary Search Tree Insertion",
    description: "Recursive ordering property and pointer updates.",
    status: "in_progress",
    mastery_score: 0.55,
    prerequisites: [],
    evidence_count: 2,
  },
  {
    id: "ml_gradient_descent",
    subject: "ai_ml",
    title: "Gradient Descent Optimization",
    description: "Step-size updates and convergence on convex loss surfaces.",
    status: "available",
    mastery_score: 0.35,
    prerequisites: ["quad_vertex"],
    evidence_count: 1,
  },
];

export const DEMO_QUESTIONS: QuestionItem[] = [
  {
    id: "q_quad_01",
    subject: "mathematics",
    concept_id: "quad_vertex",
    pattern_id: "parabola_vertex",
    difficulty: "medium",
    title: "Vertex of a Parabola",
    question_text: "Find the x-coordinate of the vertex for the parabola given by f(x) = x² - 4x + 3.",
    canonical_answer: "2",
    hint_ladder: [
      "Level 1: Recall how the axis of symmetry relates to the coefficients a and b in ax² + bx + c.",
      "Level 2: The formula for the vertex x-coordinate is x = -b / (2a). Check the sign of b carefully.",
      "Level 3: Here a = 1 and b = -4. Substitute these into x = -(-4) / (2 * 1) to complete the final calculation.",
    ],
    visual_spec: {
      schema_version: "1.0",
      type: "function_plot",
      title: "f(x) = x² - 4x + 3 with Vertex Highlight",
      viewport: { xmin: -2, xmax: 6, ymin: -3, ymax: 7 },
      axes: { x: { label: "x", grid: true }, y: { label: "y", grid: true } },
      parameters: [{ id: "a", label: "Curvature a", min: 0.5, max: 2, step: 0.5, default: 1 }],
      elements: [
        { id: "f1", kind: "function", expr: "x^2 - 4*x + 3", style: "primary", legend: "f(x) = x² - 4x + 3" },
        { id: "v1", kind: "point", x: 2, y: -1, label: "Vertex (2, -1)", derived_from: "f1.vertex" },
        { id: "r1", kind: "point", x: 1, y: 0, label: "Root (1,0)", derived_from: "f1.root" },
        { id: "r2", kind: "point", x: 3, y: 0, label: "Root (3,0)", derived_from: "f1.root" }
      ],
      annotations: [{ target: "v1", text: "Minimum Point at x = 2", kind: "callout" }],
      explanation: "The vertex represents the turning point where the tangent is horizontal."
    }
  },
  {
    id: "q_py_01",
    subject: "python",
    concept_id: "py_loops",
    pattern_id: "loop_range",
    difficulty: "easy",
    title: "Off-by-One Loop Bounds",
    question_text: "How many iterations will `for i in range(1, 5):` execute?",
    canonical_answer: "4",
    hint_ladder: [
      "Level 1: Recall whether the stop value in Python's range(start, stop) is inclusive or exclusive.",
      "Level 2: The range generates numbers starting at start and stops before reaching stop.",
      "Level 3: It generates [1, 2, 3, 4], so count the items in that sequence.",
    ]
  }
];

export const DEMO_MISCONCEPTIONS = [
  {
    id: "sign_error_vertex",
    name: "Sign Neglect in Axis of Symmetry",
    subject: "mathematics",
    wrong_rule: "Using x = b / 2a instead of x = -b / 2a",
    status: "active",
    evidence_count: 2,
    occurrences: 3,
    last_seen: "2026-11-02",
  },
  {
    id: "inclusive_range_stop",
    name: "Inclusive Range Boundary Assumption",
    subject: "python",
    wrong_rule: "Assuming range(1, N) includes N as the final iteration value",
    status: "improving",
    evidence_count: 3,
    occurrences: 4,
    last_seen: "2026-10-31",
  },
  {
    id: "bst_left_larger",
    name: "BST Ordering Inversion",
    subject: "dsa",
    wrong_rule: "Inserting elements larger than root into left subtree",
    status: "resolved",
    evidence_count: 5,
    occurrences: 2,
    last_seen: "2026-10-28",
  }
];
