"""
CLI / Script Runner for Adaption AutoScientist Workflow.
Defaults to Dry-Run mode. Uses official SDK method semantics.
"""
import sys
import os
import argparse
import json
from pathlib import Path

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

from app.modules.autoscientist.service import AutoScientistService
from app.modules.autoscientist.schemas import TrainingRunCreateRequest


def run_pipeline(dry_run: bool = True, dataset_path: str = "ml/datasets/train.jsonl", model_id: str = "meta-llama/Llama-3.1-8B-Instruct"):
    print("=" * 80)
    print(f"NEUROTEACH AI — ADAPTION AUTOSCIENTIST PIPELINE RUNNER")
    print(f"Mode: {'[DRY-RUN - SAFE MOCK]' if dry_run else '[LIVE CLOUD EXECUTION]'}")
    print(f"Target Dataset: {dataset_path}")
    print(f"Target Model: {model_id}")
    print("=" * 80)

    service = AutoScientistService(dry_run=dry_run)

    # 1. Dataset Upload
    print("\n[Step 1/6] Uploading Dataset via client.datasets.upload_file...")
    upload_res = service.upload_dataset(dataset_path)
    print(f"  -> Dataset ID: {upload_res.dataset_id}")
    print(f"  -> Upload Status: {upload_res.status}")
    print(f"  -> Verified Rows: {upload_res.row_count}")
    print(f"  -> Mock Result: {upload_res.is_mock}")

    # 2. Check Dataset Processing Status
    print("\n[Step 2/6] Checking Dataset Status via client.datasets.get_status...")
    status_res = service.check_dataset_status(upload_res.dataset_id)
    print(f"  -> Processing Status: {status_res.status.value}")
    print(f"  -> Mock Result: {status_res.is_mock}")

    # 3. List Available Models
    print("\n[Step 3/6] Listing Available Models via client.autoscientist.list_models...")
    models = service.list_available_models()
    for m in models:
        print(f"  • {m.id} ({m.display_name}) - Context: {m.context_length} tokens, Mock: {m.is_mock}")

    # 4. Get Recommended Hyperparameters
    print(f"\n[Step 4/6] Retrieving Hyperparameters via client.autoscientist.recommend_hyperparams...")
    hp = service.get_recommended_hyperparameters(dataset_id=upload_res.dataset_id, model=model_id)
    print(f"  -> Learning Rate: {hp.learning_rate}")
    print(f"  -> Epochs (n_epochs): {hp.n_epochs}")
    print(f"  -> Batch Size: {hp.batch_size}")
    print(f"  -> Warmup Ratio: {hp.warmup_ratio}")
    print(f"  -> LoRA Config: r={hp.lora_r}, alpha={hp.lora_alpha}")
    print(f"  -> Mock Result: {hp.is_mock}")

    # 5. Create Training Run
    print("\n[Step 5/6] Creating Run via client.autoscientist.create...")
    run_req = TrainingRunCreateRequest(
        dataset_id=upload_res.dataset_id,
        model=model_id,
        hyperparams=hp.model_dump(),
        run_name=f"neuroteach_sft_{upload_res.dataset_id}"
    )
    training_run = service.create_training_run(
        request=run_req,
        user_confirmed_paid_operation=not dry_run
    )
    print(f"  -> Experiment ID: {training_run.id}")
    print(f"  -> Initial Status: {training_run.status.value}")
    print(f"  -> Mock Result: {training_run.is_mock}")

    # 6. Check Run Status & Download Checkpoint
    print(f"\n[Step 6/6] Checking Status via client.autoscientist.get & download...")
    run_status = service.get_run_status(training_run.id)
    print(f"  -> Experiment Status: {run_status.status.value}")
    print(f"  -> Iterations Completed: {run_status.iterations_completed}/{run_status.max_iterations}")
    print(f"  -> Best Win Rate: {run_status.best_win_rate}")
    print(f"  -> Mock Result: {run_status.is_mock}")

    download_res = service.download_best_checkpoint(training_run.id)
    print(f"  -> Checkpoint Output: {download_res['output_dir']}")
    print(f"  -> Files: {download_res.get('files', [])}")
    print(f"  -> Mock Download: {download_res['is_mock']}")

    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION COMPLETED")
    print(f"Audit Trail saved to: {service.audit_dir.resolve()}")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoScientist Pipeline Runner")
    parser.add_argument("--live", action="store_true", help="Launch live cloud training (requires approval and API key)")
    parser.add_argument("--dataset", default="ml/datasets/train.jsonl", help="Dataset path")
    parser.add_argument("--model", default="meta-llama/Llama-3.1-8B-Instruct", help="Target model ID")
    args = parser.parse_args()

    run_pipeline(dry_run=not args.live, dataset_path=args.dataset, model_id=args.model)
