# NEUROTEACH AI — Adaption AutoScientist Stage 6.4: Training Configuration & Cost Preflight

**Audit Date**: 2026-11-02T22:02:00Z  
**Adaption SDK Version**: `adaption==0.17.1`  
**Target Dataset ID**: `0a290391-cf2a-47bb-9cb5-2e0cc83783ed` (1,080 rows, Status: `succeeded`)  
**Target Model**: `Qwen/Qwen3.5-4B`  
**Execution Mode**: **SAFE PREFLIGHT ONLY** (`ADAPTION_DRY_RUN=True`)  
**Safety Gate**: No experiment created. `client.autoscientist.create()` was not called.  

---

## 1. Task 1: SDK `create()` Signature & Parameter Audit

Inspected via Python reflection on `from adaption.resources.autoscientist import AutoscientistResource`:

```python
client.autoscientist.create(
    *,
    dataset_id: str,
    model: str | Omit = ...,
    training_method: Literal['instruction', 'alignment'] | Omit = ...,
    data_format: Literal['chat', 'instruction'] | Omit = ...,
    column_mapping: autoscientist_create_params.ColumnMapping | Omit = ...,
    hyperparams: autoscientist_create_params.Hyperparams | Omit = ...,
    augmentation_domain_rows: float | Omit = ...,
    augmentation_general_rows: float | Omit = ...,
    idempotency_key: str | Omit = ...,
    voucher: str | Omit = ...,
    max_iterations: float | Omit = ...,
    target_win_rate: float | Omit = ...,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN
) -> AutoscientistRun
```

### Parameter Mapping & Compliance
1. **`dataset_id`**: `"0a290391-cf2a-47bb-9cb5-2e0cc83783ed"` (Verified processed on Adaption Cloud).
2. **`model`**: `"Qwen/Qwen3.5-4B"` (Verified live in Adaption catalog).
3. **`training_method`**: `"instruction"` (Supervised Fine-Tuning; alignment/DPO disabled).
4. **`data_format`**: `"instruction"` (Direct `prompt` and `completion` column mapping).
5. **`column_mapping`**: `{"prompt": "prompt", "completion": "completion"}`.
6. **`max_iterations`**: `5.0` (Permits up to 5 iterative search loops).
7. **`target_win_rate`**: `0.85` (Stops early when evaluation win rate reaches 85%).
8. **`augmentation_domain_rows`**: `0.0` (No synthetic domain padding).
9. **`augmentation_general_rows`**: `0.0` (No synthetic general padding).

---

## 2. Task 2: Live Platform Hyperparameter Mapping

The live hyperparameter recommendation derived directly from AutoScientist for dataset `0a290391-cf2a-47bb-9cb5-2e0cc83783ed` maps 1:1 to `autoscientist_create_params.Hyperparams`:

| Hyperparameter Key | Platform Live Value | Supported in SDK Schema? | Implementation Role |
| :--- | :--- | :--- | :--- |
| **`training_type`** | `"lora"` | Yes (`Literal['lora', 'full']`) | PEFT parameter-efficient adapter training |
| **`n_epochs`** | `1.0` | Yes (`float`) | Training epochs derived for 1,080 SFT rows |
| **`learning_rate`** | `0.00005` ($5\times 10^{-5}$) | Yes (`float`) | Base optimizer learning rate |
| **`batch_size`** | `"max"` | Yes (`Literal['max', int]`) | Dynamically saturated to cluster GPU VRAM |
| **`lora_r`** | `16.0` | Yes (`float`) | LoRA intrinsic rank dimension |
| **`lora_alpha`** | `32.0` | Yes (`float`) | LoRA scaling coefficient |
| **`lora_dropout`** | `0.05` | Yes (`float`) | Dropout regularization on adapter matrices |
| **`lora_trainable_modules`** | `"all-linear"` | Yes (`str`) | Targets all linear projection layers |
| **`warmup_ratio`** | `0.03` | Yes (`float`) | Initial linear warmup percentage (3%) |
| **`weight_decay`** | `0.0` | Yes (`float`) | L2 weight decay penalty |
| **`lr_scheduler_type`** | `"cosine"` | Yes (`Literal['linear', 'cosine']`) | Cosine decay schedule |

---

## 3. Task 3 & 4: Model Compatibility & Dataset Status

- **Model Compatibility**:
  - `Qwen/Qwen3.5-4B` verified active on platform.
  - Context window: **262,144 tokens**.
  - Methods supported: `['sft', 'dpo']`.
  - Reasoning support: **`train_with_reasoning: True`** (crucial for pedagogical diagnosis and error tree exploration).
- **Dataset Confirmation via Live SDK**:
  - `client.datasets.get_status("0a290391-cf2a-47bb-9cb5-2e0cc83783ed")` returned:
    - `status: "succeeded"`
    - `row_count: 1080`
    - `progress: Progress(percent=100, processed_rows=1080, total_rows=1080)`
    - `error_data: None`

---

## 4. Task 5 & 6: Data Format & Evaluation Dataset Analysis

### A. Independent Parameter Semantics
- **`processing_mode="raw"`**: Used during dataset upload (`upload_file`). Materializes the local JSONL directly into a trainable dataset without synthetic adaptation.
- **`data_format="instruction"`**: Passed during training run creation (`create`). Directs the trainer to encode prompt and completion for standard instruction-completion SFT.

### B. Evaluation Dataset Support in SDK
- An exhaustive audit of `client.autoscientist.create` parameters confirmed that **no validation or evaluation dataset parameters exist in the SDK** (`val_dataset_id`, `eval_dataset_id`, etc., do not exist).
- AutoScientist's iterative optimization engine computes win rates using internal cross-validation / synthetic holdout subsets derived from the uploaded dataset.
- **Strict Compliance**: The local `ml/datasets/validated_v2/validation.jsonl` (145 rows) and `test.jsonl` (125 rows) remain strictly offline and isolated for independent local evaluation benchmarks.

---

## 5. Task 7 & 8: Checkpoint Export & Inference Backend Serving Integration

### A. Checkpoint Export Analysis
- **Download Signature**: `client.autoscientist.download(experiment_id) -> BinaryAPIResponse`.
- **Artifact Format**: A compressed archive containing a standard Hugging Face PEFT LoRA adapter:
  ```
  checkpoints/<experiment_id>/
  ├── adapter_config.json
  ├── adapter_model.safetensors
  └── tokenizer_config.json (optional)
  ```

### B. Model Serving & Integration Path
In `backend/app/modules/llm/client.py`, the current implementation is a deterministic offline simulator (`MockPedagogicalModelClient`). To connect the fine-tuned model to the live platform:

1. **Deploying the Checkpoint**:
   - Option 1 (Self-hosted vLLM with LoRA):
     ```bash
     vllm serve Qwen/Qwen3.5-4B --enable-lora --lora-modules neuroteach=artifacts/training_results/checkpoints/<experiment_id> --port 8080
     ```
   - Option 2 (Hugging Face TGI / vLLM merged weights).
2. **Backend Serving Integration (`backend/app/modules/llm/client.py`)**:
   - Implement `LivePedagogicalModelClient` with an async HTTP client (`httpx.AsyncClient`) calling `settings.MODEL_ENDPOINT_URL` (`http://localhost:8080/v1/chat/completions`).
   - Format student messages using Qwen instruction format:
     ```json
     {
       "model": "neuroteach",
       "messages": [
         {"role": "system", "content": "You are NEUROTEACH AI pedagogical tutor..."},
         {"role": "user", "content": "<JSON payload with student_attempt and learner_state>"}
       ],
       "temperature": 0.2,
       "response_format": {"type": "json_object"}
     }
     ```
   - Parse and validate the returned JSON using `ModelResponseSchema`.
   - Keep `MockPedagogicalModelClient` as an automatic fallback when the live model server is unreachable.

---

## 6. Task 9 & 10: Cost Review & Available Account Credits

### A. Account Credits Review
- **User-Reported Dashboard Status**:
  - Plus plan active (valid until January 25, 2027).
  - **Total Available Credits**: **650 credits**.
  - **Monthly Plan Allowance**: **100 credits/month**.
- **Programmatic Pricing Status**:
  - An inspection of the installed SDK confirmed that **no pricing, balance, or billing query APIs exist**.
  - **Pricing and exact per-run credit deduction CANNOT be verified programmatically via the SDK**.
  - Training runs on AutoScientist consume compute credits from the user's 650 balance based on GPU time and iteration count.

### B. Candidate Configuration Artifact
Saved to: [artifacts/training_results/training_config_candidate.json](file:///d:/oracathon/artifacts/training_results/training_config_candidate.json)

---

## 7. Safety Status & Approval Checkpoint

- **Safety Gate**: Active. `ADAPTION_DRY_RUN=True` preserved.
- **`PermissionError` Guard**: In live mode, `create_training_run` enforces `user_confirmed_paid_operation=True`.
- **Status**: Preflight complete. Ready for explicit user confirmation before launching live training.
