import json
import os

print("=== TASK 1: DATASET AUDIT ON EXISTING DATASETS ===")
splits = ["train", "val", "test"]
for split in splits:
    path = os.path.join("ml", "datasets", "backup", f"{split}.jsonl")
    if not os.path.exists(path):
        print(f"Missing {path}")
        continue

    count = 0
    subjects = {}
    misconceptions = {}
    strategies = {}
    first_keys = []
    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            count += 1
            rec = json.loads(line)
            if count == 1:
                first_keys = list(rec.keys())
            
            subj = rec.get("subject", "unknown")
            subjects[subj] = subjects.get(subj, 0) + 1
            
            exp_out = rec.get("expected_output", {})
            diag = exp_out.get("diagnosis", {})
            mis_id = diag.get("misconception_id", "none")
            misconceptions[mis_id] = misconceptions.get(mis_id, 0) + 1
            
            strat = exp_out.get("strategy", {}).get("name", "none")
            strategies[strat] = strategies.get(strat, 0) + 1

    print(f"\n--- Split: {split} (Total rows: {count}) ---")
    print("Keys in record:", first_keys)
    print("Subjects:", subjects)
    print("Misconceptions:", misconceptions)
    print("Strategies:", strategies)
