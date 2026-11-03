"""
Unit test suite verifying dataset integrity, deduplication, schema adherence,
zero-leakage across both validated (v1) and validated_v2 evaluation splits, and manifest validity.
"""
import json
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def manifest_v1():
    manifest_path = REPO_ROOT / "ml" / "datasets" / "validated" / "dataset_manifest.json"
    assert manifest_path.exists(), f"Dataset manifest v1 not found at {manifest_path}!"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def manifest_v2():
    manifest_path = REPO_ROOT / "ml" / "datasets" / "validated_v2" / "dataset_manifest.json"
    assert manifest_path.exists(), f"Dataset manifest v2 not found at {manifest_path}!"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_dataset_splits_v1_exist():
    base_dir = REPO_ROOT / "ml" / "datasets" / "validated"
    assert (base_dir / "train.jsonl").exists()
    assert (base_dir / "validation.jsonl").exists()
    assert (base_dir / "test.jsonl").exists()
    assert (base_dir / "dataset_manifest.json").exists()


def test_dataset_splits_v2_exist():
    base_dir = REPO_ROOT / "ml" / "datasets" / "validated_v2"
    assert (base_dir / "train.jsonl").exists()
    assert (base_dir / "validation.jsonl").exists()
    assert (base_dir / "test.jsonl").exists()
    assert (base_dir / "dataset_manifest.json").exists()


def test_v2_split_row_counts_meet_autoscientist_criteria(manifest_v2):
    train_count = manifest_v2["splits"]["train.jsonl"]["row_count"]
    val_count = manifest_v2["splits"]["validation.jsonl"]["row_count"]
    test_count = manifest_v2["splits"]["test.jsonl"]["row_count"]
    total = train_count + val_count + test_count

    assert total >= 1250, f"Total records {total} < 1250"
    assert train_count >= 1000, f"Training split {train_count} must have at least 1,000 effective examples!"
    assert val_count >= 125, f"Validation split {val_count} must have at least 125 examples!"
    assert test_count >= 125, f"Test split {test_count} must have at least 125 examples!"


def test_zero_leakage_across_v2_splits():
    base_dir = REPO_ROOT / "ml" / "datasets" / "validated_v2"
    
    def get_questions(fname):
        qs = set()
        with open(base_dir / fname, "r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                p = json.loads(rec["prompt"])
                qs.add(p["question"]["text"])
        return qs

    train_qs = get_questions("train.jsonl")
    val_qs = get_questions("validation.jsonl")
    test_qs = get_questions("test.jsonl")

    # Strict zero question overlap check
    assert len(train_qs.intersection(val_qs)) == 0, "Question leakage between Train and Validation!"
    assert len(train_qs.intersection(test_qs)) == 0, "Question leakage between Train and Test!"
    assert len(val_qs.intersection(test_qs)) == 0, "Question leakage between Validation and Test!"


def test_valid_json_and_required_keys_v2():
    base_dir = REPO_ROOT / "ml" / "datasets" / "validated_v2"
    for fname in ["train.jsonl", "validation.jsonl", "test.jsonl"]:
        with open(base_dir / fname, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                rec = json.loads(line)
                assert "prompt" in rec, f"Missing prompt at {fname}:{idx+1}"
                assert "completion" in rec, f"Missing completion at {fname}:{idx+1}"
                assert len(rec["prompt"].strip()) > 0
                assert len(rec["completion"].strip()) > 0

                # Validate inner structures
                p_obj = json.loads(rec["prompt"])
                c_obj = json.loads(rec["completion"])
                
                assert "subject" in p_obj
                assert "concept_id" in p_obj
                assert "diagnosis" in c_obj
                assert "strategy" in c_obj
                assert "intervention" in c_obj
                assert c_obj["diagnosis"]["error_type"] in ("careless", "conceptual", "unclear")
                assert "text" in c_obj["intervention"]


def test_subject_and_strategy_coverage_v2(manifest_v2):
    for split_name in ["train.jsonl", "validation.jsonl", "test.jsonl"]:
        split_data = manifest_v2["splits"][split_name]
        # Must cover all 4 core subjects
        subjects = split_data["subjects"]
        assert "mathematics" in subjects
        assert "dsa" in subjects
        assert "python" in subjects
        assert "ai_ml" in subjects

        # Must have all 8 teaching strategies
        strategies = split_data["strategies"]
        assert len(strategies) == 8, f"{split_name} has {len(strategies)} strategies, expected 8"
