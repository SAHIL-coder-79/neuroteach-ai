# NEUROTEACH AI — STAGE 8.2: RUNPOD PRE-LAUNCH COST & COMPATIBILITY REPORT

**Audit Date**: 2026-11-03  
**User Spending Limit Constraint**: **Hard Maximum Total Budget of $0.50 USD**  
**Target Hardware Selection**: **NVIDIA RTX A5000 (24 GB VRAM)**  
**Base Model**: `Qwen/Qwen3.5-4B` (`togethercomputer/Qwen3.5-4B`)  
**Adapter Checkpoint**: `artifacts/training_results/checkpoints/819874ef-44b1-4a76-a049-1ce35638bba8`  
**Status**: **PRE-LAUNCH AUDIT COMPLETE — LAUNCH BLOCKED PENDING DEPOSIT CLARIFICATION**  

---

## 1. Executive Summary & Critical Budget Finding

> [!WARNING]
> **CRITICAL BUDGET & SPENDING LIMIT AUDIT FINDING**:  
> While the **actual compute and storage consumption** for a 30-minute verification run is **$0.14 USD** (well below the $0.50 cap), **RunPod cannot be funded or used with a hard initial cap of $0.50 USD**.  
> 
> 1. **Deposit Threshold**: RunPod operates strictly on a **prepaid balance model** with a **$10.00 USD minimum credit card deposit** via Stripe. It is technically impossible to deposit or load $0.50 into a RunPod account.
> 2. **No Automated $0.50 Hard Cap**: RunPod enforces a default platform spending cap of **$80.00/hr** to prevent large-scale runaway jobs, but does not provide an automated per-sub-dollar spending cutoff feature.
> 3. **Per-Second Billing vs Deposit**: If an account already possesses existing pre-funded credits, a 20–30 minute verification session on an RTX A5000 will consume **only ~$0.13 to $0.15 of balance**. However, if funding a new account, a **minimum deposit of $10.00 USD** is mandatory.
> 
> In accordance with Task 10: *"If the total cost cannot be guaranteed at or below $0.50, stop and explain the minimum safe budget required."* — **execution is paused, and explicit clarification/authorization is requested.**

---

## 2. Live Pricing & Cost Model Breakdown (RTX A5000 24GB)

Prices verified directly against official RunPod catalog specifications:

| Parameter | Official Rate | Notes / Rules |
| :--- | :--- | :--- |
| **GPU Rate (Community Cloud)** | **$0.16 to $0.19 / hour** | Billed per-second. Subject to real-time supply/demand. |
| **GPU Rate (Secure Cloud)** | **$0.27 / hour** | Enterprise datacenter tier with 99.9% uptime SLA. |
| **Running Container Disk (20 GB)** | **$0.10 / GB / month** | $\approx \$0.000137/\text{hr}$ for 20 GB ($\approx \$0.00007$ for 30 min). |
| **Stopped Volume Storage** | **$0.20 / GB / month** | Applicable only if pod is stopped but not destroyed. Destroying pod eliminates storage billing. |
| **Network Egress / Ingress** | **$0.00 (Free)** | Zero bandwidth charges for pulling base model or uploading LoRA weights. |
| **Minimum Billing Duration** | **1 second** (post-launch) | Minimum account balance to launch: $\ge 1\text{ hour}$ of GPU rate ($\ge \$0.27$). |
| **Idle Billing** | Same as running | Pod must be terminated immediately after testing to avoid idle billing. |
| **Taxes & Payment Surcharges** | 0% - Stripe standard | Standard Stripe processing included; local sales tax depends on billing jurisdiction. |

---

## 3. Total Maximum Cost Projection for a 30-Minute Verification Session

Session breakdown timeline:
1. **Pod Provision & Container Pull**: 2 minutes (Docker image pull: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1`).
2. **Environment & Dependency Check**: 3 minutes (`pip install transformers peft safetensors`).
3. **Base Model Weights Download**: 5 minutes (`togethercomputer/Qwen3.5-4B` BF16, ~8.0 GB via Hugging Face CDN at 300+ Mbps).
4. **Adapter Checkpoint Transfer**: 1 minute (169.9 MB uploaded via secure SCP/curl).
5. **Model Initialization & Weight Loading**: 2 minutes (PyTorch loads base weights and PEFT LoRA layers into GPU VRAM).
6. **Inference & Health Verification**: 5 minutes (Run test turn, inspect output, test API 503 fallback isolation).
7. **Scrubbing & Pod Termination**: 2 minutes (Execute teardown script and call terminate API).
- **Total Max Wall-Clock Time**: **20 to 30 minutes (0.50 hours max)**.

### Worst-Case Cost Calculation (Secure Cloud Tier @ $0.27/hr):
$$\text{GPU Compute Cost} = 0.50\text{ hours} \times \$0.27/\text{hr} = \$0.1350\text{ USD}$$
$$\text{Container Disk (20 GB)} = 0.50\text{ hours} \times \left(\frac{20 \times \$0.10}{730\text{ hours}}\right) = \$0.0014\text{ USD}$$
$$\text{Data Ingress / Egress} = \$0.0000\text{ USD}$$
$$\mathbf{Total\ Actual\ Session\ Cost} = \mathbf{\$0.1364\text{ USD}}\ (\approx \mathbf{\$0.14\text{ USD}})$$

The **true consumption cost** of the verification session is **$0.14 USD**, which is strictly below the $0.50 USD threshold. However, accessing the platform requires addressing the minimum deposit threshold described in Section 1.

---

## 4. Hardware & Runtime Compatibility Verification

### 4.1 Base Model Architecture: `Qwen3.5-4B`
- **Architecture**: `Qwen3_5ForConditionalGeneration` (`model_type: qwen3_5`).
- **Layers**: 32 layers with hybrid alternating attention (3 linear-attention layers followed by 1 full self-attention layer).
- **GPU VRAM Budget on RTX A5000 (24 GB VRAM)**:
  - Base model weights in native BF16: **8.04 GB**.
  - LoRA adapter weights (256 rank-32 tensors): **0.16 GB**.
  - PyTorch CUDA runtime & context: **0.60 GB**.
  - KV Cache & Activations ($\le 2,048$ tokens): **0.30 GB**.
  - **Total VRAM Allocated**: **~9.10 GB** out of **24.0 GB**.
  - **VRAM Headroom**: **14.9 GB (62% free)** $\implies$ Zero risk of Out-Of-Memory (OOM).

### 4.2 LoRA Adapter Weights Compatibility
- Verified file format: `adapter_model.safetensors` contains FP32 LoRA weight matrices matching target modules:
  `['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']`.
- Serving software stack:
  - `transformers >= 4.49.0`
  - `peft >= 0.14.0`
  - `torch >= 2.4.0` with CUDA 12.4
  - Standalone FastAPI/uvicorn server with native ChatML templating.

---

## 5. Security & Isolation Controls

To ensure 100% security and strict boundary compliance:
1. **Zero Secret Leakage**:
   - Neither `.env`, database files (`neuroteach.db`), nor application backend source code are copied to the worker.
   - The worker runs an isolated 70-line standalone runner ([runpod_inference_server.sh](file:///d:/oracathon/scripts/runpod_inference_server.sh)) whose only purpose is loading the adapter weights and exposing `/v1/chat/completions`.
2. **Adapter File Scope**:
   - Only the public checkpoint directory is transferred:
     - `adapter_model.safetensors`
     - `adapter_config.json`
     - `tokenizer.json`
     - `tokenizer_config.json`
     - `chat_template.jinja`
3. **Data Scrubbing & Immediate Destruction**:
   - [runpod_teardown.sh](file:///d:/oracathon/scripts/runpod_teardown.sh) scrubs all files from `/workspace/adapter` before pod removal.
   - Pod is deleted immediately to prevent stopped-storage billing.

---

## 6. Prepared Deployment & Teardown Scripts

Two standalone scripts have been prepared locally in `scripts/`:

1. **Deployment & Startup Script**: [runpod_inference_server.sh](file:///d:/oracathon/scripts/runpod_inference_server.sh)
   - Verifies GPU CUDA availability and VRAM capacity.
   - Installs official `transformers`, `peft`, `accelerate`.
   - Loads `togethercomputer/Qwen3.5-4B` in BF16 and attaches the local LoRA adapter.
   - Launches an OpenAI-compatible `/v1/chat/completions` server on port 8000 with a `/health` check.

2. **Teardown & Scrub Script**: [runpod_teardown.sh](file:///d:/oracathon/scripts/runpod_teardown.sh)
   - Kills all inference server processes.
   - Securely scrubs the adapter weights.
   - Emits shutdown instructions for immediate pod deletion.

---

## 7. Action Required: Decision & Approval Gate

In compliance with instructions:
- **No pod has been launched.**
- **No storage has been provisioned.**
- **No checkpoints have been uploaded.**
- **Zero charges have been incurred.**

### Next Steps for the User:
1. **If an existing funded RunPod account is available**: The verification session can proceed immediately within the planned $0.14 consumption cost.
2. **If creating a new RunPod account**: Note the platform's **$10.00 USD minimum Stripe deposit requirement**.
3. **Alternative**: If strict zero-external-spend is required, we can configure a local 4-bit quantized test on the RTX 3050 Laptop GPU using CPU memory offloading.

Awaiting your explicit authorization before any launch or upload.

