import json
import os
import sys

sys.path.insert(0, os.path.abspath("backend"))

from app.modules.visual.validator import VisualSpecValidator
from app.modules.policy.engine import TeachingPolicyEngine

def audit_dataset():
    print("=== TASK 3: FULL DATASET AUDIT & QUALITY VERIFICATION ===")
    splits = ["train", "validation", "test"]
    
    total_stats = {}
    train_prompts = set()
    train_misconceptions = set()
    test_misconceptions = set()
    
    leakage_failures = 0
    spec_validation_failures = 0
    invalid_json_count = 0
    duplicate_count = 0

    seen_hashes = set()

    for split in splits:
        path = os.path.join("ml", "datasets", f"{split}.jsonl")
        rows = 0
        subjects = {}
        strategies = {}
        error_types = {}
        has_visual_count = 0

        with open(path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                rows += 1
                try:
                    data = json.loads(line)
                except Exception:
                    invalid_json_count += 1
                    continue

                prompt = data.get("prompt", "")
                completion = data.get("completion", "")
                meta = data.get("meta", {})

                # Check duplicates
                h = hash((prompt, completion))
                if h in seen_hashes:
                    duplicate_count += 1
                else:
                    seen_hashes.add(h)

                if split == "train":
                    train_prompts.add(prompt)
                    if meta.get("misconception_id"):
                        train_misconceptions.add(meta["misconception_id"])
                elif split == "test":
                    if meta.get("misconception_id"):
                        test_misconceptions.add(meta["misconception_id"])

                # Metrics
                subj = meta.get("subject", "unknown")
                subjects[subj] = subjects.get(subj, 0) + 1
                strat = meta.get("strategy", "unknown")
                strategies[strat] = strategies.get(strat, 0) + 1
                err_t = meta.get("error_type", "unknown")
                error_types[err_t] = error_types.get(err_t, 0) + 1
                if meta.get("has_visual"):
                    has_visual_count += 1

                # Deterministic answer leakage check on hint
                comp_obj = json.loads(completion)
                intervention = comp_obj.get("intervention", {}).get("text", "")
                canonical_ans = meta.get("canonical_answer", "")
                if TeachingPolicyEngine.detect_answer_leakage(intervention, canonical_ans):
                    leakage_failures += 1
                    if leakage_failures <= 3:
                        print(f"DEBUG LEAK [{split} {data.get('id')}]: canonical='{canonical_ans}' text='{intervention}'")

                # Deterministic visual spec check
                spec = comp_obj.get("visual_spec")
                if spec:
                    is_valid, _ = VisualSpecValidator.validate_spec(spec)
                    if not is_valid:
                        spec_validation_failures += 1

        total_stats[split] = {
            "rows": rows,
            "subjects": subjects,
            "strategies": strategies,
            "error_types": error_types,
            "has_visual_count": has_visual_count,
        }

    # Leakage check between train and test
    test_leakage_overlap = train_misconceptions.intersection(test_misconceptions)

    print("\n--- Summary Statistics ---")
    for split, s in total_stats.items():
        print(f"\n[{split.upper()}] Rows: {s['rows']}")
        print(f"  Subjects: {s['subjects']}")
        print(f"  Strategies: {s['strategies']}")
        print(f"  Error Types: {s['error_types']}")
        print(f"  Visual Questions: {s['has_visual_count']}")

    print("\n--- Integrity & Verification Results ---")
    print(f"Invalid JSON Lines: {invalid_json_count}")
    print(f"Duplicates Detected: {duplicate_count}")
    print(f"Answer Leakage Failures: {leakage_failures}")
    print(f"Visual Spec Validation Failures: {spec_validation_failures}")
    print(f"Train/Test Misconception Overlap (Target: 0): {len(test_leakage_overlap)} {test_leakage_overlap}")

    return total_stats, {
        "invalid_json": invalid_json_count,
        "duplicates": duplicate_count,
        "leakage_failures": leakage_failures,
        "spec_failures": spec_validation_failures,
        "test_overlap": list(test_leakage_overlap),
    }

if __name__ == "__main__":
    audit_dataset()
