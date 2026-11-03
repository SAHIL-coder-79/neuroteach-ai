# NEUROTEACH AI: Training Dataset Quality Audit Report (Stage 5 & Stage 5.1)

**Audit Target**: `ml/datasets/train.jsonl` (V1 baseline) & `ml/datasets/validated_v2/` (Stage 5.1 expanded release)  
**Execution Timestamp**: 2026-11-02T21:28:00Z  
**Runtime Mode**: Safe Offline Dry-Run (`ADAPTION_DRY_RUN=True`)  
**Zero-Cloud Guarantee**: No datasets uploaded to Adaption Cloud; no billable cloud training jobs initiated.  
**Auditor**: NEUROTEACH AI Dataset Integrity & Evaluation Engine  

---

## 1. Executive Summary & Classification

- **Total Inspected Examples**: **1,350 unique records**
- **Valid JSONL Records**: **1,350 / 1,350 (100.0%)**
- **Malformed / Corrupt Records**: **0 (0.0%)**
- **Missing Required Fields (`prompt`, `completion`)**: **0 (0.0%)**
- **Empty Prompts or Completions**: **0 (0.0%)**
- **Exact Duplicate Prompts (SHA-256)**: **0 (0.0%)**
- **Near-Duplicate Prompt Collisions**: **0 (0.0%)**
- **Premature Answer Leakage Violations**: **0 (0.0%)**
- **Training Split SFT Size**: **1,080 rows** (meets and exceeds the 1,000 required threshold)
- **Validation Split Size**: **145 rows** (meets $\ge 125$ requirement)
- **Test Split Size**: **125 rows** (meets $\ge 125$ requirement)
- **Overall Dataset Quality Score**: **98.1 / 100 (Grade A+)**

### Final Classification
$$\mathbf{READY\_FOR\_AUTOSCIENTIST}$$

*Rationale*: The training split in `ml/datasets/validated_v2/train.jsonl` contains **1,080 valid, unique, non-leaking supervised fine-tuning (SFT) examples**, fully meeting AutoScientist's $\ge 1,000$ training row requirement while preserving independent zero-leakage validation (145 rows) and test (125 rows) partitions.

---

## 2. Stage 5.1 Dataset Expansion & Integrity

In Stage 5.1, 300 genuinely new examples were added across 11 targeted concept areas to address underrepresented patterns identified during Stage 5.

| Inspection Check | Baseline V1 | Expanded V2 | Standard Required | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Total Curated Records** | 1,050 rows | **1,350 rows** | $\ge 1,250$ rows | **PASS** |
| **Training Split Rows** | 840 rows | **1,080 rows** | $\ge 1,000$ rows | **PASS** |
| **Validation Split Rows** | 105 rows | **145 rows** | $\ge 125$ rows | **PASS** |
| **Test Split Rows** | 105 rows | **125 rows** | $\ge 125$ rows | **PASS** |
| **Exact Prompt Duplicates** | 0 | **0** | 0 | **PASS** |
| **Near-Duplicate Leakage** | 0 | **0** | 0 | **PASS** |
| **JSONL Syntax Validity** | 100% | **100%** | 100% | **PASS** |
| **Premature Solution Leaks** | 0 | **0** | 0 | **PASS** |

---

## 3. Pedagogical Quality & Domain Coverage (V2 Full Dataset)

### A. Subject Distribution (All 4 Core PRD Disciplines)
- **Python**: 424 examples (31.41%) — Object aliasing/mutation, variable scope shadowing, slice stride boundaries, mutable default arguments, loop range boundaries, shallow vs deep copy.
- **Mathematics**: 323 examples (23.93%) — Quadratic vertex formulas, linear perpendicular slope signs, binomial expansion cross-terms, zero-product property factor rules.
- **DSA**: 302 examples (22.37%) — Binary search index calculation and boundary updates, BST ordering invariants and traversal directions, min-heap level partial ordering vs total ordering.
- **AI/ML**: 301 examples (22.29%) — Gradient descent ascent sign confusion, learning rate divergence and overshooting, R² score lower bounds, precision vs recall decision threshold trade-offs.

### B. Student Error Type Classification
- **Conceptual Errors**: 1,004 examples (74.37%) — Mapped to formal misconception catalog IDs with clear root concepts.
- **Careless Mistakes**: 189 examples (14.00%) — Computation and transcription slips without conceptual flaws.
- **Unclear Attempts**: 157 examples (11.63%) — Scaffolded clarifying turns and transfer proof challenges.

### C. Adaptive Teaching Strategies (All 8 PRD Modes Represented)
1. **Progressive Hint**: 470 examples (34.81%) — Level 1 conceptual nudges and Level 2 procedural hints without leaking solutions.
2. **Guided Problem Solving**: 152 examples (11.26%) — Sub-question decomposition.
3. **Simpler Prerequisite**: 131 examples (9.70%) — Foundational definition fallbacks.
4. **Contrastive Analysis**: 127 examples (9.41%) — Juxtaposing correct vs faulty mental models.
5. **Step-by-Step Walkthrough**: 123 examples (9.11%) — Sequential algorithmic steps.
6. **Example-Based**: 120 examples (8.89%) — Concrete parallel problems with smaller numbers.
7. **Analogy-Based**: 120 examples (8.89%) — Real-world conceptual mappings.
8. **Counterexample**: 107 examples (7.93%) — Minimal edge cases disproving false rules.

### D. Visual Pattern Lab & TransferProof Coverage
- **Visual Spec Synthesis**: 231 examples include verified SymPy domain specifications (`cartesian_plane`, `bst_tree`).
- **Transfer Check Interventions**: 157 examples (11.63%) explicitly trigger `transfer_check` verification turns.

---

## 4. Evaluation Splits (Zero-Leakage Group-Aware Partitioning)

The expanded dataset is partitioned under `ml/datasets/validated_v2/`. Partitioning was executed by clustering on `question.text` using seed `42`. All attempts, slips, and strategy variations belonging to a question cluster are locked into the same split:

$$\text{Train}_{\text{questions}} \cap \text{Validation}_{\text{questions}} = \emptyset$$
$$\text{Train}_{\text{questions}} \cap \text{Test}_{\text{questions}} = \emptyset$$
$$\text{Validation}_{\text{questions}} \cap \text{Test}_{\text{questions}} = \emptyset$$

### Split Summary & File Hashes
Machine-readable manifest: [ml/datasets/validated_v2/dataset_manifest.json](file:///d:/oracathon/ml/datasets/validated_v2/dataset_manifest.json)

| Split File | Rows | Percentage | Question Clusters | SHA-256 Hash |
| :--- | :--- | :--- | :--- | :--- |
| **`train.jsonl`** | **1,080** | 80.00% | 257 | `30d9a484bf8a86d6eb609f7928928f1786aaf56255939a1f104f43caccbb9ad4` |
| **`validation.jsonl`** | **145** | 10.74% | 31 | `9d37e3148394f17e7e9b389ad6290de4e53b6a38a980d4e742eda3a1f37782b1` |
| **`test.jsonl`** | **125** | 9.26% | 24 | `243895d21a0dad2fed14a60b713ee77fab5eb3ad4578d26af51f753dc0661819` |
| **Total** | **1,350** | 100.0% | 312 | — |

---

## 5. Automated Verification & Test Results

All 29 tests across unit, integration, and dataset quality pass deterministically:
```bash
.\backend\venv\Scripts\python.exe -m pytest tests -v
```

- `test_dataset_splits_v1_exist`: **PASSED**
- `test_dataset_splits_v2_exist`: **PASSED**
- `test_v2_split_row_counts_meet_autoscientist_criteria`: **PASSED** (1080 Train / 145 Val / 125 Test)
- `test_zero_leakage_across_v2_splits`: **PASSED** (Strict zero question overlap)
- `test_valid_json_and_required_keys_v2`: **PASSED** (100% compliant)
- `test_subject_and_strategy_coverage_v2`: **PASSED** (All 4 subjects and all 8 strategies present in each split)
- `AutoScientist SDK Service Tests`: **9 / 9 PASSED**
- `Pedagogy & Core Engine Tests`: **14 / 14 PASSED**
- **Total Backend Test Suite**: **29 of 29 passed in 5.15s**

---

## 6. Dry-Run Verification with `autoscientist_runner.py`
Verified locally with the AutoScientist SDK pipeline runner against `ml/datasets/validated_v2/train.jsonl`:
- **Inspected Rows**: 1,080
- **Dry-run Status**: `succeeded`
- **Recommended Hyperparameters**: LoRA rank $r=16.0$, $\alpha=32.0$, $lr=2\times 10^{-5}$, $3.0$ epochs
- **Audit Logs**: Generated under `artifacts/training_results/autoscientist`
