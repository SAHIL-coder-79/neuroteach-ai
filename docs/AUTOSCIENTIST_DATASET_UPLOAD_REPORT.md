# NEUROTEACH AI — Adaption AutoScientist Dataset Upload Report (Stage 6.3)

**Execution Status**: **SUCCESSFUL**  
**Execution Timestamp**: 2026-11-02T16:28:22Z  
**Adaption SDK Version**: `adaption==0.17.1`  
**Training Gate**: **PRESERVED** (No training run created; zero experiments launched)  

---

## 1. Executive Summary

In accordance with Stage 6.3 instructions and explicit user authorization, **ONLY** the supervised fine-tuning training dataset (`ml/datasets/validated_v2/train.jsonl`) was uploaded to Adaption Cloud.

- **Assigned Dataset ID**: `0a290391-cf2a-47bb-9cb5-2e0cc83783ed`
- **Dataset Name**: `neuroteach_ai_sft_train_v2`
- **Processing Status**: **`succeeded` (100% processed)**
- **Verified Cloud Row Count**: **1,080 rows**
- **Excluded Datasets**: `validation.jsonl` (145 rows) and `test.jsonl` (125 rows) remain strictly local.
- **Safety Gate**: No experiment was dispatched. `client.autoscientist.create()` was not called.

---

## 2. Pre-Upload Cryptographic & File Verification

Prior to dispatching network requests, local integrity was verified:

| Check | Specification | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| **Target Path** | `ml/datasets/validated_v2/train.jsonl` | `D:\oracathon\ml\datasets\validated_v2\train.jsonl` | **PASS** |
| **SHA-256 Hash** | `30d9a484bf8a86d6eb609f7928928f1786aaf56255939a1f104f43caccbb9ad4` | `30d9a484bf8a86d6eb609f7928928f1786aaf56255939a1f104f43caccbb9ad4` | **PASS** |
| **Row Count** | Exactly 1,080 rows | 1,080 non-empty JSONL lines | **PASS** |
| **Column Structure** | Valid `prompt` and `completion` keys on all rows | 1,080 / 1,080 valid JSON strings | **PASS** |
| **Split Isolation** | Validation & Test datasets excluded | 145 Val rows & 125 Test rows kept offline | **PASS** |
| **API Key Status** | Present in backend environment | Valid key masked (`pt_live_b0c4...`) | **PASS** |

---

## 3. Upload Execution Details

The upload was dispatched using the official SDK invocation:
```python
client.datasets.upload_file(
    path="D:/oracathon/ml/datasets/validated_v2/train.jsonl",
    name="neuroteach_ai_sft_train_v2",
    processing_mode="raw",
    column_mapping={
        "prompt": "prompt",
        "completion": "completion"
    }
)
```

- **Initial Response**: Status `pending`, returned `dataset_id: "0a290391-cf2a-47bb-9cb5-2e0cc83783ed"`.
- **Status Polling**:
  - `T+0s`: Status: `pending`
  - `T+8s`: Status: `succeeded` | Rows: `1080` | Progress: `Progress(percent=100, processed_rows=1080, total_rows=1080)`
- **Cloud Ingestion Verification**: All 1,080 rows were successfully validated, tokenized, and materialized as a trainable dataset on the Adaption platform.

---

## 4. Live Platform Hyperparameter Recommendation

Following successful dataset ingestion, a live read-only query to `client.autoscientist.recommend_hyperparams(dataset_id="0a290391-cf2a-47bb-9cb5-2e0cc83783ed", model="Qwen/Qwen3.5-4B")` was performed:

| Hyperparameter | Live Platform Derived Value | Notes |
| :--- | :--- | :--- |
| **Base Model** | `Qwen/Qwen3.5-4B` | Target 4B parameter foundation model with native reasoning |
| **Training Type** | `lora` | Parameter-Efficient Fine-Tuning |
| **LoRA Rank ($r$)** | `16.0` | Balanced representation capacity |
| **LoRA Alpha ($\alpha$)** | `32.0` | Scaling factor ($\alpha / r = 2.0$) |
| **Epochs (`n_epochs`)** | `1.0` | Derived by platform for 1,080-row instruction SFT |
| **Learning Rate** | `5e-05` ($0.00005$) | Optimized for Qwen 3.5 architecture |
| **Batch Size** | `max` | Sized dynamically to available GPU VRAM |
| **Warmup Ratio** | `0.03` ($3\%$) | Linear learning rate warmup |
| **Weight Decay** | `0.0` | No L2 regularization on adapter weights |
| **LR Scheduler Type** | `cosine` | Cosine annealing schedule |

---

## 5. Artifact Audit Trail

Audit metadata is stored locally at:
- [artifacts/training_results/datasets/dataset_upload_0a290391-cf2a-47bb-9cb5-2e0cc83783ed.json](file:///d:/oracathon/artifacts/training_results/datasets/dataset_upload_0a290391-cf2a-47bb-9cb5-2e0cc83783ed.json)

---

## 6. Safety Gate Confirmation

- **No Experiment Dispatched**: `client.autoscientist.create()` was **NOT** called.
- **Credit Balance Preserved**: Only dataset ingestion took place; no training GPU time was consumed.
- **Stage 6.3 Complete**: All requirements achieved. Awaiting future instructions before any training execution.
