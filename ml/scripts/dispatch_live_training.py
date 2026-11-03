"""
Live AutoScientist Training Dispatch and Monitoring Script (Stage 7.1).
Dispatches the authorized training run, polls status until terminal,
downloads the checkpoint upon success, extracts LoRA weights,
and generates full metadata artifacts.
"""
import os
import sys
import time
import json
import hashlib
import tarfile
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load backend .env securely
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env")))

from adaption import Adaption


def execute_live_training():
    print("=" * 80)
    print("NEUROTEACH AI — STAGE 7.1: LIVE AUTOSCIENTIST TRAINING DISPATCH")
    print("=" * 80)

    api_key = os.getenv("ADAPTION_API_KEY", "")
    if not api_key:
        raise ValueError("ADAPTION_API_KEY is not configured in backend/.env!")

    client = Adaption(api_key=api_key, timeout=120.0)

    dataset_id = "0a290391-cf2a-47bb-9cb5-2e0cc83783ed"
    model_id = "Qwen/Qwen3.5-4B"
    idempotency_key = "neuroteach_qwen4b_0a290391_v1"

    print("\n[Step 1/5] Checking for Existing Experiments (Idempotency Safety)...")
    existing_run = None
    try:
        runs = client.autoscientist.list()
        all_runs = list(runs) if hasattr(runs, "__iter__") else getattr(runs, "data", [])
        for r in all_runs:
            # Check matching dataset or model if available
            if getattr(r, "dataset_id", None) == dataset_id:
                existing_run = r
                print(f"  -> Found existing experiment on dataset {dataset_id}: ID = {r.id}, Status = {r.status}")
                break
    except Exception as e:
        err_msg = str(e)
        if api_key in err_msg:
            err_msg = err_msg.replace(api_key, "[REDACTED]")
        print(f"  Note during runs list: {err_msg}")

    run_obj = None
    if existing_run:
        print(f"  -> Reconciled existing experiment: {existing_run.id}. Skipping duplicate create() call.")
        run_obj = existing_run
    else:
        print("\n[Step 2/5] Calling client.autoscientist.create() with Authorized Payload...")
        create_payload = {
            "dataset_id": dataset_id,
            "model": model_id,
            "training_method": "instruction",
            "data_format": "instruction",
            "column_mapping": {
                "prompt": "prompt",
                "completion": "completion"
            },
            "hyperparams": {
                "training_type": "lora",
                "n_epochs": 1.0,
                "learning_rate": 0.00005,
                "batch_size": "max",
                "lora_r": 16.0,
                "lora_alpha": 32.0,
                "lora_dropout": 0.05,
                "lora_trainable_modules": "all-linear",
                "warmup_ratio": 0.03,
                "weight_decay": 0.0,
                "lr_scheduler_type": "cosine"
            },
            "max_iterations": 5.0,
            "target_win_rate": 0.85,
            "augmentation_domain_rows": 0.0,
            "augmentation_general_rows": 0.0,
            "idempotency_key": idempotency_key
        }

        try:
            run_obj = client.autoscientist.create(**create_payload)
            print(f"  -> DISPATCH SUCCESS! Returned Experiment ID: {run_obj.id}")
            print(f"  -> Initial Status: {run_obj.status}")
        except Exception as e:
            err_msg = str(e)
            if api_key in err_msg:
                err_msg = err_msg.replace(api_key, "[REDACTED]")
            print(f"  -> Error during create(): {err_msg}")
            # Try to reconcile if created remotely before timeout
            try:
                runs = client.autoscientist.list()
                all_runs = list(runs) if hasattr(runs, "__iter__") else getattr(runs, "data", [])
                for r in all_runs:
                    if getattr(r, "dataset_id", None) == dataset_id:
                        run_obj = r
                        print(f"  -> Reconciled newly created run: {run_obj.id}")
                        break
            except Exception:
                pass
            if not run_obj:
                raise RuntimeError(f"Training dispatch failed: {err_msg}")

    experiment_id = run_obj.id
    print(f"\n[Step 3/5] Monitoring Training Experiment: {experiment_id}...")

    terminal_statuses = {"succeeded", "failed", "cancelled"}
    poll_interval = 15
    last_status = getattr(run_obj, "status", "pending")
    latest_run = run_obj

    start_time = time.time()
    while True:
        try:
            latest_run = client.autoscientist.get(experiment_id=experiment_id)
            current_status = getattr(latest_run, "status", "unknown").lower()
            iters = getattr(latest_run, "iterations_completed", 0.0)
            max_iters = getattr(latest_run, "max_iterations", 5.0)
            win_rate = getattr(latest_run, "best_win_rate", None)
            download_avail = getattr(latest_run, "download_available", False)

            elapsed_min = round((time.time() - start_time) / 60, 1)
            print(f"  [T+{elapsed_min}m] Status: {current_status.upper()} | Iterations: {iters}/{max_iters} | Best Win Rate: {win_rate} | Download Available: {download_avail}")

            if current_status in terminal_statuses:
                print(f"\n  -> Terminal State Reached: {current_status.upper()}!")
                break
        except Exception as e:
            err_msg = str(e)
            if api_key in err_msg:
                err_msg = err_msg.replace(api_key, "[REDACTED]")
            print(f"  Transient polling warning: {err_msg}. Retrying in {poll_interval}s...")

        time.sleep(poll_interval)

    # Persist live run metadata
    out_dir = Path("artifacts/training_results/live_runs")
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path = out_dir / f"experiment_{experiment_id}.json"

    meta_record = {
        "experiment_id": experiment_id,
        "dataset_id": dataset_id,
        "model": getattr(latest_run, "model", model_id),
        "status": getattr(latest_run, "status", "unknown"),
        "training_method": getattr(latest_run, "training_method", "instruction"),
        "created_at": str(getattr(latest_run, "created_at", "")),
        "completed_at": str(getattr(latest_run, "completed_at", "")),
        "iterations_completed": getattr(latest_run, "iterations_completed", 0.0),
        "max_iterations": getattr(latest_run, "max_iterations", 5.0),
        "target_win_rate": getattr(latest_run, "target_win_rate", 0.85),
        "best_win_rate": getattr(latest_run, "best_win_rate", None),
        "download_available": getattr(latest_run, "download_available", False),
        "error": getattr(latest_run, "error", None),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_record, f, indent=2)

    print(f"Run metadata persisted to {meta_path.resolve()}")

    if getattr(latest_run, "status", "").lower() != "succeeded":
        print(f"\nExperiment did not succeed. Final Status: {latest_run.status}. Error: {getattr(latest_run, 'error', None)}")
        return meta_record

    # 4. Checkpoint Download
    print(f"\n[Step 4/5] Downloading Checkpoint for Succeeded Experiment {experiment_id}...")
    ckpt_dir = Path(f"artifacts/training_results/checkpoints/{experiment_id}")
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    archive_path = ckpt_dir / "checkpoint_raw.bin"

    download_resp = client.autoscientist.download(experiment_id=experiment_id)
    download_resp.write_to_file(str(archive_path.resolve()))
    print(f"  -> Checkpoint archive downloaded: {archive_path.stat().st_size} bytes")

    # 5. Extract Adapter Safely
    print("\n[Step 5/5] Extracting LoRA Adapter Artifacts...")
    extracted_files = []
    
    # Try tar or zip extraction
    is_tar = False
    try:
        with tarfile.open(archive_path, "r:*") as tar:
            tar.extractall(path=ckpt_dir)
            extracted_files = tar.getnames()
            is_tar = True
            print(f"  -> Extracted tar archive: {extracted_files}")
    except Exception:
        pass

    if not is_tar:
        try:
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(path=ckpt_dir)
                extracted_files = zf.namelist()
                print(f"  -> Extracted zip archive: {extracted_files}")
        except Exception as e:
            print(f"  -> Raw binary archive saved directly (not standard tar/zip): {e}")

    # Inspect extracted files and calculate SHA-256
    file_hashes = {}
    for item in ckpt_dir.rglob("*"):
        if item.is_file() and item.name != "checkpoint_raw.bin":
            sha256 = hashlib.sha256()
            with open(item, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    sha256.update(chunk)
            file_hashes[item.name] = {
                "size_bytes": item.stat().st_size,
                "sha256": sha256.hexdigest(),
                "relative_path": str(item.relative_to(ckpt_dir)),
            }
            print(f"     • {item.name}: {item.stat().st_size} bytes | SHA-256: {sha256.hexdigest()}")

    meta_record["checkpoint_files"] = file_hashes
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_record, f, indent=2)

    print("\n" + "=" * 80)
    print("STAGE 7.1 LIVE TRAINING RUN COMPLETED SUCCESSFULLY!")
    print(f"Experiment ID: {experiment_id}")
    print(f"Artifacts Directory: {ckpt_dir.resolve()}")
    print("=" * 80)

    return meta_record


if __name__ == "__main__":
    execute_live_training()
