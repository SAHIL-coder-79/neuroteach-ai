# Dataset Quality & Integrity Report — NEUROTEACH AI

**Generated Date**: 2026-11-02  
**Dataset Version**: `neuroteach-sft-v1`  
**Target Platform**: Adaption AutoScientist  

---

## 1. Executive Summary & Row Counts

| Dataset Split | File Path | Total Rows | Effective Training Rows | Status |
|---|---|---|---|---|
| **Train** | `ml/datasets/train.jsonl` | **1,050** | **1,050** | ✅ Verified |
| **Validation** | `ml/datasets/validation.jsonl` | **150** | — | ✅ Verified |
| **Held-Out Test** | `ml/datasets/test.jsonl` | **200** | — | ✅ Frozen (Held-Out) |
| **Total Corpus** | — | **1,400** | **1,050** | ✅ Clean & Ready |

*Note: The original prototype dataset files (350 train, 50 val, 100 test) have been backed up in `ml/datasets/backup/`.*

---

## 2. Integrity, Quality & Leakage Audit Results

| Audit Check | Metric / Target | Result | Status |
|---|---|---|---|
| **JSONL Syntax Validity** | 0 malformed lines | **0 invalid lines** | ✅ Passed |
| **Duplicate Examples** | 0 duplicates (prompt + completion) | **0 duplicates** | ✅ Passed |
| **Answer Leakage Failures** | $\le 2\%$ on hints | **0 failures (0.0%)** | ✅ Passed |
| **Visual Spec Validation Failures** | 100% SymPy verification | **0 failures (0.0%)** | ✅ Passed |
| **Train / Test Misconception Overlap** | 0 overlap (Strict generalization) | **0 overlapping IDs** | ✅ Passed |

---

## 3. Distribution Breakdown across Splits

### A. Subject Distribution
| Subject | Train Split (1,050) | Validation Split (150) | Test Split (200) |
|---|---|---|---|
| **Python** | 340 (32.4%) | 37 (24.7%) | — |
| **DSA** | 221 (21.0%) | 34 (22.7%) | 63 (31.5%) |
| **AI / ML** | 247 (23.5%) | 41 (27.3%) | — |
| **Mathematics** | 242 (23.0%) | 38 (25.3%) | 137 (68.5%) |

### B. Teaching Strategy Distribution (Train Split)
- **Progressive Hint**: 346 (33.0%)
- **Guided Problem Solving**: 123 (11.7%)
- **Simpler Prerequisite**: 106 (10.1%)
- **Contrastive Examples**: 104 (9.9%)
- **Step-by-Step**: 98 (9.3%)
- **Example-Based**: 93 (8.9%)
- **Analogy**: 92 (8.8%)
- **Counterexample**: 88 (8.4%)

### C. Error Mode Distribution (Train Split)
- **Conceptual Errors**: 798 (76.0%)
- **Careless Slips**: 148 (14.1%)
- **Unclear / Probing Steps**: 104 (9.9%)

---

## 4. Deterministic Verification Methodology
1. **Mathematical Accuracy**: All coordinate geometry and parabola roots are generated using symbolic parameter expansions ($b = -2h$, $c = h^2 + k$).
2. **Deterministic Visual Spec Validation**: 100% of generated `visual_spec` objects passed the 7-step pipeline:
   - Pydantic schema validation.
   - SymPy AST whitelist symbols (`x`, `y`, `sin`, `cos`, `sqrt`, `exp`, etc.).
   - 200-point domain sampling without singularity errors.
   - Dynamic polynomial degree & vertex recomputation ($\le 10^{-3}$ numeric diff).
3. **Strict Evaluation Isolation**: The 200 test items contain misconceptions entirely withheld from training (`root_product_zero`, `exponent_distribution`, `heap_sorted_levels`), ensuring benchmark results reflect true pedagogical generalization.
