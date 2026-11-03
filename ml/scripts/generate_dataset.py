import json
import random
import os
import sys
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath("backend"))

from app.modules.misconceptions.catalog import MISCONCEPTION_CATALOG
from app.modules.policy.engine import TEACHING_STRATEGIES
from app.modules.visual.patterns import PatternLibrary

def generate_synthetic_record(example_id: str, split: str) -> Dict[str, Any]:
    misconception_keys = list(MISCONCEPTION_CATALOG.keys())
    # Stratified test holdout: reserve first 2 misconceptions exclusively for test
    if split == "test":
        chosen_mis_id = random.choice(misconception_keys[:2])
    else:
        chosen_mis_id = random.choice(misconception_keys[2:])

    item = MISCONCEPTION_CATALOG[chosen_mis_id]
    strategy = random.choice(TEACHING_STRATEGIES)

    q_data = PatternLibrary.generate_parabola_vertex_question(difficulty=random.choice(["easy", "medium", "hard"]))

    return {
        "id": example_id,
        "split": split,
        "task": "teach_turn",
        "subject": item.subject,
        "concept_id": item.concept_id,
        "question": {
            "id": f"q_{example_id}",
            "text": q_data["question_text"],
            "pattern_id": q_data["pattern_id"],
            "canonical_answer": q_data["canonical_answer"],
            "visual_spec": q_data["visual_spec"],
        },
        "student_attempt": {
            "answer": "-2" if item.id == "sign_error_vertex" else "0",
            "reasoning": f"I followed the rule: {item.wrong_rule}",
            "correct": False,
        },
        "learner_state": {
            "mastery": round(random.uniform(0.1, 0.6), 2),
            "active_misconceptions": [item.id],
            "hint_level_used": 1,
            "strategies_tried": [{"name": "progressive_hint", "outcome": "fail"}],
            "recent_accuracy": 0.4
        },
        "expected_output": {
            "diagnosis": {
                "error_type": "conceptual",
                "misconception_id": item.id,
                "confidence": 0.88,
                "evidence": item.wrong_rule,
                "root_concepts": item.root_concepts,
                "explanation": item.description,
            },
            "strategy": {
                "name": strategy,
                "rationale": f"Adaptive selection of {strategy} for {item.name}",
                "hint_level": 2 if strategy == "progressive_hint" else None,
            },
            "intervention": {
                "text": f"Let's test this intuition: {item.counterexample}",
                "asks_student_to": "inspect the counterexample and re-evaluate",
            },
            "visual_spec": q_data["visual_spec"],
            "next_check": {"type": "observe_reply"}
        }
    }

def build_datasets():
    os.makedirs("ml/datasets", exist_ok=True)

    print("Generating stratified datasets for Adaption AutoScientist...")
    splits = {
        "train": 350,
        "val": 50,
        "test": 100 # Frozen held-out evaluation set
    }

    for split_name, count in splits.items():
        filepath = f"ml/datasets/{split_name}.jsonl"
        with open(filepath, "w", encoding="utf-8") as f:
            for i in range(count):
                rec = generate_synthetic_record(f"{split_name}_{i+1:04d}", split_name)
                f.write(json.dumps(rec) + "\n")
        print(f"Generated {count} records in {filepath}")

if __name__ == "__main__":
    build_datasets()
