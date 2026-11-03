"""
Live Dataset Upload Script for Adaption Cloud (Stage 6.3).
Uploads ONLY ml/datasets/validated_v2/train.jsonl (1,080 rows).
Strictly excludes validation.jsonl and test.jsonl.
Does NOT create training runs or billable experiments.
"""
import os
import sys
import time
import json
import hashlib
from pathlib import Path
from dotenv import load_dotenv

# Load backend environment variables
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env")))

from adaption import Adaption


def execute_live_dataset_upload(
    file_path: str = "ml/datasets/validated_v2/train.jsonl",
    dataset_name: str = "neuroteach_ai_sft_train_v2",
    target_model: str = "Qwen/Qwen3.5-4B",
):
    print("=" * 80)
    print("NEUROTEACH AI — STAGE 6.3: LIVE DATASET UPLOAD TO ADAPTION CLOUD")
    print("=" * 80)

    api_key = os.getenv("ADAPTION_API_KEY", "")
    if not api_key:
        raise ValueError("ADAPTION_API_KEY is not configured in backend/.env!")

    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"Target file not found at {file_path}")

    # 1. Verification of Hash and Row Count
    print("\n[Step 1/5] Verifying Target File Integrity...")
    sha256 = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    actual_hash = sha256.hexdigest()
    expected_hash = "30d9a484bf8a86d6eb609f7928928f1786aaf56255939a1f104f43caccbb9ad4"
    if actual_hash != expected_hash:
        raise ValueError(f"Hash mismatch! Calculated: {actual_hash} vs Expected: {expected_hash}")

    with open(p, "r", encoding="utf-8") as f:
        rows = [line.strip() for line in f if line.strip()]
    row_count = len(rows)
    if row_count != 1080:
        raise ValueError(f"Expected exactly 1,080 rows, found {row_count}")

    print(f"  • File: {p.resolve()}")
    print(f"  • Verified Rows: {row_count}")
    print(f"  • SHA-256 Match: True ({actual_hash})")
    print(f"  • API Key Present: True (Prefix: {api_key[:7]}...)")

    # 2. Initialize Client
    print("\n[Step 2/5] Initializing Adaption SDK Client...")
    client = Adaption(api_key=api_key, timeout=120.0)

    # 3. Upload File
    print(f"\n[Step 3/5] Uploading '{p.name}' with processing_mode='raw'...")
    upload_resp = client.datasets.upload_file(
        path=str(p.resolve()),
        name=dataset_name,
        processing_mode="raw",
        column_mapping={
            "prompt": "prompt",
            "completion": "completion"
        }
    )

    dataset_id = getattr(upload_resp, "dataset_id", str(upload_resp))
    initial_status = getattr(upload_resp, "status", "pending")
    print(f"  -> Returned Dataset ID: {dataset_id}")
    print(f"  -> Initial Upload Status: {initial_status}")

    # 4. Poll Dataset Processing Status
    print(f"\n[Step 4/5] Polling Processing Status for Dataset '{dataset_id}'...")
    final_status_resp = None
    max_wait_seconds = 300
    start_time = time.time()

    while time.time() - start_time < max_wait_seconds:
        status_resp = client.datasets.get_status(dataset_id=dataset_id)
        current_status = getattr(status_resp, "status", "pending").lower()
        processed_rows = getattr(status_resp, "row_count", None)
        progress = getattr(status_resp, "progress", None)

        print(f"  [T+{int(time.time() - start_time)}s] Status: '{current_status}' | Rows: {processed_rows} | Progress: {progress}")

        if current_status in ("succeeded", "ready", "processed"):
            final_status_resp = status_resp
            break
        elif current_status in ("failed", "error"):
            err_data = getattr(status_resp, "error_data", None)
            raise RuntimeError(f"Dataset processing failed: {err_data}")

        time.sleep(5)

    if not final_status_resp:
        raise TimeoutError(f"Dataset processing timed out after {max_wait_seconds} seconds.")

    print(f"  -> Processing Complete! Final Status: '{final_status_resp.status}'")
    print(f"  -> Processed Row Count: {final_status_resp.row_count}")

    # 5. Live Hyperparameter Recommendation Check
    print(f"\n[Step 5/5] Querying Hyperparameter Recommendation for Model '{target_model}'...")
    recommended_hp_dict = None
    try:
        hp_resp = client.autoscientist.recommend_hyperparams(
            dataset_id=dataset_id,
            model=target_model
        )
        hp = getattr(hp_resp, "hyperparams", None)
        recommended_hp_dict = {
            "model": getattr(hp_resp, "model", target_model),
            "training_type": getattr(hp, "training_type", None),
            "n_epochs": getattr(hp, "n_epochs", None),
            "learning_rate": getattr(hp, "learning_rate", None),
            "batch_size": getattr(hp, "batch_size", None),
            "lora_r": getattr(hp, "lora_r", None),
            "lora_alpha": getattr(hp, "lora_alpha", None),
            "warmup_ratio": getattr(hp, "warmup_ratio", None),
            "weight_decay": getattr(hp, "weight_decay", None),
            "lr_scheduler_type": getattr(hp, "lr_scheduler_type", None),
        }
        print("  -> Live Derived Hyperparameters from AutoScientist:")
        for k, v in recommended_hp_dict.items():
            print(f"     • {k}: {v}")
    except Exception as e:
        err_msg = str(e)
        if api_key in err_msg:
            err_msg = err_msg.replace(api_key, "[REDACTED]")
        print(f"  -> Hyperparameter query returned notice: {err_msg}")

    # Save audit record
    audit_record = {
        "dataset_id": dataset_id,
        "dataset_name": dataset_name,
        "filename": p.name,
        "source_path": str(p.resolve()),
        "sha256": actual_hash,
        "row_count": final_status_resp.row_count,
        "status": str(final_status_resp.status),
        "target_model": target_model,
        "recommended_hyperparameters": recommended_hp_dict,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    audit_dir = Path("artifacts/training_results/datasets")
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_file = audit_dir / f"dataset_upload_{dataset_id}.json"
    with open(audit_file, "w", encoding="utf-8") as f:
        json.dump(audit_record, f, indent=2)

    print("\n" + "=" * 80)
    print("LIVE DATASET UPLOAD & VERIFICATION COMPLETED SUCCESSFULLY!")
    print(f"Audit saved to: {audit_file.resolve()}")
    print("=" * 80)

    return audit_record


if __name__ == "__main__":
    execute_live_dataset_upload()
