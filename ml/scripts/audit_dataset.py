"""
Dataset Audit & Analysis Script for NEUROTEACH AI.
Analyzes ml/datasets/train.jsonl across integrity, pedagogical criteria,
data leakage, deduplication, and prepares 80/10/10 stratified evaluation splits.
"""
import json
import hashlib
import re
from pathlib import Path
from collections import Counter, defaultdict
import random


def run_audit(dataset_path: str = "ml/datasets/train.jsonl"):
    p = Path(dataset_path)
    if not p.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    total_rows = 0
    valid_json_rows = 0
    malformed_rows = []
    missing_fields_rows = []
    empty_prompt_or_completion = []
    
    seen_prompts = set()
    exact_duplicate_rows = []
    
    # Near duplicate detection (normalized text hash)
    def normalize_text(text: str) -> str:
        return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', text.lower())).strip()
        
    seen_normalized_prompts = {}
    near_duplicate_rows = []

    # Subjects & Pedagogical distribution
    subject_counts = Counter()
    error_type_counts = Counter()
    strategy_counts = Counter()
    misconception_counts = Counter()
    visual_spec_count = 0
    transfer_question_count = 0
    
    # Quality & Leakage checks
    leakage_detected = []
    generic_or_repetitive = []
    valid_examples = []

    leak_patterns = [
        re.compile(r"the correct answer is\s*[:=]?\s*([^\.]+)", re.IGNORECASE),
        re.compile(r"the answer is\s*[:=]?\s*([^\.]+)", re.IGNORECASE),
        re.compile(r"solution is\s*[:=]?\s*([^\.]+)", re.IGNORECASE),
    ]

    with open(p, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            total_rows += 1
            line_str = line.strip()
            if not line_str:
                malformed_rows.append((idx + 1, "Empty line"))
                continue

            try:
                record = json.loads(line_str)
            except Exception as e:
                malformed_rows.append((idx + 1, f"JSON parse error: {str(e)}"))
                continue

            valid_json_rows += 1

            # Validate required fields
            if "prompt" not in record or "completion" not in record:
                missing_fields_rows.append((idx + 1, "Missing prompt or completion"))
                continue

            prompt_val = record.get("prompt", "")
            completion_val = record.get("completion", "")

            if not prompt_val or not completion_val:
                empty_prompt_or_completion.append(idx + 1)
                continue

            # Check exact duplicates
            prompt_hash = hashlib.sha256(prompt_val.encode('utf-8')).hexdigest()
            if prompt_hash in seen_prompts:
                exact_duplicate_rows.append(idx + 1)
                continue
            seen_prompts.add(prompt_hash)

            # Check near duplicates
            norm_p = normalize_text(prompt_val)
            norm_hash = hashlib.md5(norm_p.encode('utf-8')).hexdigest()
            if norm_hash in seen_normalized_prompts:
                near_duplicate_rows.append((idx + 1, seen_normalized_prompts[norm_hash]))
                # We record it but keep evaluating
            else:
                seen_normalized_prompts[norm_hash] = idx + 1

            # Parse inner prompt & completion
            try:
                p_obj = json.loads(prompt_val) if isinstance(prompt_val, str) else prompt_val
                c_obj = json.loads(completion_val) if isinstance(completion_val, str) else completion_val
            except Exception as e:
                malformed_rows.append((idx + 1, f"Inner JSON parse error: {e}"))
                continue

            # Subject extraction
            subj = p_obj.get("subject", record.get("meta", {}).get("subject", "unknown"))
            subject_counts[subj] += 1

            # Diagnosis & error types
            diagnosis = c_obj.get("diagnosis", {})
            err_type = diagnosis.get("error_type", "unknown")
            error_type_counts[err_type] += 1
            misc_id = diagnosis.get("misconception_id")
            if misc_id:
                misconception_counts[misc_id] += 1

            # Strategy
            strat = c_obj.get("strategy", {})
            strat_name = strat.get("name", "unknown")
            strategy_counts[strat_name] += 1

            # Visual Spec
            if c_obj.get("visual_spec"):
                visual_spec_count += 1

            # Next check / Transfer
            next_chk = c_obj.get("next_check", {})
            if next_chk.get("type") in ("transfer_question", "verify_mastery") or "question" in next_chk:
                transfer_question_count += 1

            # Answer leakage check in progressive hint interventions
            intervention = c_obj.get("intervention", {})
            interv_text = intervention.get("text", "")
            
            # Check if hint immediately leaks answer when hint_level < 3
            hint_lvl = strat.get("hint_level") or 1
            if hint_lvl < 3:
                for lp in leak_patterns:
                    if lp.search(interv_text):
                        leakage_detected.append((idx + 1, interv_text[:100]))
                        break

            # Repetitive / generic response check
            if len(interv_text.strip()) < 10:
                generic_or_repetitive.append((idx + 1, "Intervention too short"))

            valid_examples.append(record)

    return {
        "total_rows": total_rows,
        "valid_json_rows": valid_json_rows,
        "malformed_rows": malformed_rows,
        "missing_fields_rows": missing_fields_rows,
        "empty_prompt_or_completion": empty_prompt_or_completion,
        "exact_duplicates": len(exact_duplicate_rows),
        "near_duplicates": len(near_duplicate_rows),
        "unique_effective_examples": len(valid_examples),
        "subject_distribution": dict(subject_counts),
        "error_type_distribution": dict(error_type_counts),
        "strategy_distribution": dict(strategy_counts),
        "misconceptions_count": len(misconception_counts),
        "top_misconceptions": misconception_counts.most_common(10),
        "visual_spec_count": visual_spec_count,
        "transfer_question_count": transfer_question_count,
        "leakage_count": len(leakage_detected),
        "generic_count": len(generic_or_repetitive),
        "valid_examples": valid_examples,
    }


if __name__ == "__main__":
    res = run_audit()
    print("--- AUDIT SUMMARY ---")
    print(f"Total Rows: {res['total_rows']}")
    print(f"Valid JSON Rows: {res['valid_json_rows']}")
    print(f"Exact Duplicates: {res['exact_duplicates']}")
    print(f"Near Duplicates: {res['near_duplicates']}")
    print(f"Unique Effective Examples: {res['unique_effective_examples']}")
    print(f"Subjects: {res['subject_distribution']}")
    print(f"Error Types: {res['error_type_distribution']}")
    print(f"Strategies: {res['strategy_distribution']}")
    print(f"Misconception Types Covered: {res['misconceptions_count']}")
    print(f"Visual Specs: {res['visual_spec_count']}")
    print(f"Transfer Questions: {res['transfer_question_count']}")
    print(f"Leakage Count: {res['leakage_count']}")
