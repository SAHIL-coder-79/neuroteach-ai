# Dataset Card: NEUROTEACH AI Supervised Fine-Tuning Corpus

## 1. Dataset Summary
- **Dataset Name**: `neuroteach-sft-v1`
- **Intended Platform**: Adaption AutoScientist (Adaptive Data co-optimization & LoRA instruction tuning)
- **Language**: English
- **Domain**: Computer Science, Information Technology, and Engineering Mathematics (Python, DSA, AI/ML, Mathematics)
- **Format**: JSON Lines (`.jsonl`) containing paired `prompt` and `completion` fields with additional `id`, `split`, and verification `meta` tags.

---

## 2. Dataset Structure & Schema
Each line in `train.jsonl`, `validation.jsonl`, and `test.jsonl` contains:
```json
{
  "id": "train_0001",
  "split": "train",
  "prompt": "{\"task\":\"teach_turn\",\"subject\":\"mathematics\",\"concept_id\":\"quadratic.vertex\",...}",
  "completion": "{\"diagnosis\":{...},\"strategy\":{...},\"intervention\":{...},\"visual_spec\":{...}}",
  "meta": {
    "subject": "mathematics",
    "concept_id": "quadratic.vertex",
    "misconception_id": "sign_error_vertex",
    "strategy": "counterexample",
    "error_type": "conceptual",
    "canonical_answer": "2",
    "has_visual": true
  }
}
```

---

## 3. Splits & Leakage Prevention Strategy
To prevent test contamination and measure actual generalization:
- **Test Set (`test.jsonl`)**: 200 held-out examples strictly reserved for final evaluation. Contains 100% held-out misconceptions (e.g. `root_product_zero`, `exponent_distribution`, `heap_sorted_levels`) never exposed to training or validation.
- **Validation Set (`validation.jsonl`)**: 150 examples grouped by problem seed.
- **Train Set (`train.jsonl`)**: 1,050 high-quality multi-task instructional examples.
- **Overlap**: **0% misconception overlap** between train and test.

---

## 4. Multi-Task Capabilities Represented
1. **Misconception Diagnosis**: Multi-signal classification of `careless` (14.1%), `conceptual` (76.0%), and `unclear` (9.9%).
2. **Adaptive Strategy Selection**: Balanced coverage across all 8 strategies (Progressive Hint, Step-by-Step, Example-based, Counterexample, Contrastive, Analogy, Simpler Prerequisite, Guided Problem Solving).
3. **Scaffolded Non-Leaking Interventions**: Level 1 to 3 hints that withhold the final answer.
4. **Deterministic Visual Specifications**: Structured JSON Schema v1 specs for function plots verified with SymPy.
5. **Transfer & Similar Questions**: Problem variations testing near, medium, and far transfer.
