"""
Continuous Monitor and Checkpoint Download Script for Live Experiment 819874ef-44b1-4a76-a049-1ce35638bba8.
Polls status until terminal (succeeded, failed, cancelled),
downloads the winning model checkpoint upon completion,
extracts adapter artifacts, and writes complete metadata.
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

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env")))

from adaption import Adaption


def monitor_and_download():
    api_key = os.getenv("ADAPTION_API_KEY", "")
    if not api_key:
        raise ValueError("ADAPTION_API_KEY is not configured!")

    client = Adaption(api_key=api_key, timeout=120.0)
    experiment_id = "819874ef-44b1-4a76-a049-1ce35638bba8"
    dataset_id = "0a290391-cf2a-47bb-9cb5-2e0cc83783ed"
    model_id = "Qwen/Qwen3.5-4B"

    print("=" * 80)
    print(f"MONITORING LIVE EXPERIMENT: {experiment_id}")
    print("=" * 80)

    terminal_statuses = {"succeeded", "failed", "cancelled"}
    poll_interval = 20
    start_time = time.time()
    latest_run = None

    while True:
        try:
            latest_run = client.autoscientist.get(experiment_id=experiment_id)
            status = getattr(latest_run, "status", "unknown").lower()
            iters = getattr(latest_run, "iterations_completed", 0.0)
            max_iters = getattr(latest_run, "max_iterations", 5.0)
            win_rate = getattr(latest_run, "best_win_rate", None)
            dl_avail = getattr(latest_run, "download_available", False)

            elapsed_min = round((time.time() - start_time) / 60, 1)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] T+{elapsed_min}m | Status: {status.upper()} | Iterations: {iters}/{max_iters} | Win Rate: {win_rate} | Download Available: {dl_avail}")

            if status in terminal_statuses:
                print(f"\nTerminal state reached: {status.upper()}!")
                break
        except Exception as e:
            err_msg = str(e)
            if api_key in err_msg:
                err_msg = err_msg.replace(api_key, "[REDACTED]")
            print(f"Transient polling warning: {err_msg}")

        time.sleep(poll_interval)

    # Persist live metadata
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

    if getattr(latest_run, "status", "").lower() == "succeeded":
        print(f"\n[Checkpoint Download] Initiating download for experiment {experiment_id}...")
        ckpt_dir = Path(f"artifacts/training_results/checkpoints/{experiment_id}")
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        archive_path = ckpt_dir / "checkpoint_raw.bin"

        download_resp = client.autoscientist.download(experiment_id=experiment_id)
        download_resp.write_to_file(str(archive_path.resolve()))
        print(f"  -> Checkpoint archive downloaded: {archive_path.stat().st_size} bytes")

        # Extract archive safely
        extracted = []
        try:
            with tarfile.open(archive_path, "r:*") as tar:
                tar.extractall(path=ckpt_dir)
                extracted = tar.getnames()
        except Exception:
            try:
                with zipfile.ZipFile(archive_path, "r") as zf:
                    zf.extractall(path=ckpt_dir)
                    extracted = zf.namelist()
            except Exception as e:
                print(f"  -> Raw binary format saved directly: {e}")

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
                print(f"  • {item.name}: {item.stat().st_size} bytes | SHA-256: {sha256.hexdigest()}")

        meta_record["checkpoint_files"] = file_hashes

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_record, f, indent=2)

    print(f"\nMetadata saved to: {meta_path.resolve()}")
    return meta_record


if __name__ == "__main__":
    monitor_and_download()
