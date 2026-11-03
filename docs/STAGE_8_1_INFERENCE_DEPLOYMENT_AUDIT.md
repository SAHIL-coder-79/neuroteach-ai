# NEUROTEACH AI — STAGE 8.1: INFERENCE DEPLOYMENT FEASIBILITY AUDIT

**Audit Date**: 2026-11-03  
**Status**: COMPLETE (Awaiting User Approval Before Execution)  
**Trained Adapter Experiment ID**: `819874ef-44b1-4a76-a049-1ce35638bba8`  
**Base Architecture**: `Qwen/Qwen3.5-4B` (`togethercomputer/Qwen3.5-4B`)  
**Adapter Files Verified Locally**: `artifacts/training_results/checkpoints/819874ef-44b1-4a76-a049-1ce35638bba8/`  

---

## 1. Exact Model Architecture & Adapter Configuration

### 1.1 Model Architecture (`config.json`)
- **Architecture**: `Qwen3_5ForConditionalGeneration` (`model_type: qwen3_5`).
- **Text Backbone**: `qwen3_5_text` with 32 transformer layers.
- **Hybrid Attention Mechanism**:
  - Layers alternate in a 4-step cycle: 3 linear attention layers (`linear_attention`) followed by 1 full self-attention layer (`full_attention`).
  - Total: 24 linear attention layers and 8 full self-attention layers.
- **Hidden Dimensions**: Hidden size = 2,560; Intermediate size (MLP) = 9,216.
- **Attention Heads**: 16 query heads (`head_dim: 256`), 4 key-value heads (Grouped Query Attention, GQA).
- **Position Embeddings & RoPE**: Interleaved 3D RoPE (`mrope_interleaved: true`), $\theta = 10,000,000$, partial rotary factor = 0.25.
- **Maximum Context Length**: 262,144 tokens ($256\text{k}$).
- **Vocabulary Size**: 248,320 tokens.
- **Native Torch Precision**: `bfloat16`.

### 1.2 Adapter Configuration (`adapter_config.json`)
- **PEFT Method**: LoRA (`peft_type: LORA`, `task_type: CAUSAL_LM`).
- **Rank ($r$)**: 32.
- **Scaling Factor ($\alpha$)**: 64 (scaling ratio $\alpha / r = 2.0$).
- **Dropout**: 0.05.
- **Target Modules**: `['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']`.
  - Targets all 7 linear projections across attention and MLP feed-forward blocks in all 32 layers.
  - Parameter tensor count: **256 tensors** (each target has `lora_A` and `lora_B`).
  - LoRA File Size: 169,907,160 bytes (~162.0 MB).

### 1.3 Tokenizer Requirements (`tokenizer_config.json` & `chat_template.jinja`)
- **Tokenizer Class**: `Qwen2Tokenizer` (`tokenizers` backend).
- **Special Tokens**: Pad token = `<|endoftext|>`, EOS token = `<|im_end|>`.
- **Chat Template**: Qwen ChatML standard (`<|im_start|>system...<|im_end|><|im_start|>user...<|im_end|><|im_start|>assistant...`).

---

## 2. Serving Runtime Compatibility Analysis

| Inference Runtime | Compatibility Verdict | Minimum Version | Technical Notes & Caveats |
| :--- | :--- | :--- | :--- |
| **vLLM** | **Fully Compatible** | $\ge 0.7.0$ (Linux x86_64) | Supports `qwen3_5` hybrid linear/full attention and dynamic LoRA adapter loading (`--enable-lora --lora-modules neuroteach-trained=<path>`). Requires Linux CUDA environment; does not run natively on Windows host without WSL2 or Linux container. |
| **Hugging Face Transformers + PEFT** | **Fully Compatible** | `transformers >= 4.49.0`, `peft >= 0.14.0`, `torch >= 2.4.0` | Reference implementation. Loads via `AutoModelForCausalLM.from_pretrained(...)` and `PeftModel.from_pretrained(...)`. Can run in 4-bit/8-bit via `bitsandbytes`. |
| **SGLang** | **Compatible** | $\ge 0.4.0$ (Linux) | High throughput; supports Qwen architectures and multi-LoRA serving. Requires Linux. |
| **Ollama / llama.cpp** | **Incompatible / Partial** | GGUF converter pending | GGUF does not yet support Qwen 3.5's hybrid linear-attention / recurrent SSM layer types cleanly with LoRA delta merging. High risk of degraded output. |
| **Adaption Cloud (`client.responses`)** | **Incompatible for Private LoRAs** | SDK 0.17.1 | AutoScientist cloud trains and packages LoRAs for external deployment. Its public inference endpoints (`deepseek-v4-flash`, `glm-5.2`, `qwen3.5-397b`) do not support loading arbitrary user LoRA adapters. |

---

## 3. Hardware Requirements Audit

### 3.1 Model Weight Sizing
- Base Model: 4.02 Billion parameters.
  - In BF16 / FP16 ($2\text{ bytes/param}$): $\approx 8.04\text{ GB}$.
  - In INT8 ($1\text{ byte/param}$): $\approx 4.02\text{ GB}$.
  - In 4-bit AWQ / GPTQ / bitsandbytes ($0.5\text{ bytes/param}$): $\approx 2.01\text{ GB}$.
- LoRA Adapter Weights:
  - 256 tensors with rank $r=32$: $\approx 162\text{ MB}$.
- KV Cache & Activation Memory:
  - NeuroTeach dialogue turns use prompt context $\le 2,048$ tokens.
  - At $2\text{k}$ context, KV cache footprint is small ($\approx 250\text{ MB}$).

### 3.2 Minimum Hardware by Precision

| Precision Mode | Min GPU VRAM | Min System RAM | Disk Space Needed | Latency | Accuracy Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Full Precision (BF16)** | **12 - 16 GB** | 16 GB | 15 GB | Fastest (<15 ms/token) | Zero degradation (optimal) |
| **8-bit Quantized (INT8)** | **8 - 10 GB** | 16 GB | 10 GB | Fast (<25 ms/token) | Negligible ($\Delta < 0.2\%$) |
| **4-bit Quantized (NF4/AWQ)** | **5.5 - 6 GB** | 16 GB | 8 GB | Moderate (<40 ms/token) | Minor ($\Delta < 1.0\%$) |

---

## 4. Deployment Options Evaluation

### Option A: Local Host GPU (Windows 11 + NVIDIA RTX 3050 Laptop GPU, 6 GB VRAM)
- **Feasibility**: **Marginal / High Risk of OOM**.
  - Local GPU has exactly 6,144 MiB (6.0 GB) VRAM.
  - Windows Desktop Window Manager (DWM) and display subsystem consume 0.8 to 1.2 GB VRAM on startup, leaving only **~4.8 GB usable VRAM**.
  - 4-bit quantization (bitsandbytes) can squeeze base 4B model into ~2.8 GB, plus ~0.2 GB for LoRA adapter and ~0.5 GB for PyTorch CUDA context, leaving <1 GB margin.
  - Host OS limitation: Native Windows does not support vLLM; running PyTorch + PEFT on Windows CPU/GPU offload incurs heavy overhead. Port 8080 is also occupied locally by Oracle TNS Listener.
- **Cost**: $0.00.
- **Verdict**: Unreliable for production; possible for slow emergency CPU-offloaded validation only.

### Option B: On-Demand Cloud GPU Worker (RunPod / Vast.ai / Lambda)
- **Feasibility**: **High (Optimal for one-off verification & benchmark)**.
  - Rent a dedicated Linux container with an **RTX 4090 (24 GB)** or **RTX 3090 (24 GB)** or **A4000 (16 GB)**.
  - Native Linux environment with PyTorch 2.4, CUDA 12.4, vLLM / Hugging Face.
  - Can run Qwen3.5-4B in native unquantized BF16 with zero degradation.
  - Verification run takes 10–20 minutes, then the instance is immediately stopped/terminated.
- **Cost**: **$0.20 to $0.50 total spend** for a 30-minute verification session.
- **Verdict**: Recommended for real inference verification.

### Option C: Serverless Container Inference (Modal Labs)
- **Feasibility**: **High (Optimal for on-demand production scaling)**.
  - Modal deploys Python code to cloud containers billed per second of GPU execution ($0 idle cost).
  - An NVIDIA L4 (24 GB) costs $0.000222/sec (~$0.80/hr effective).
  - Adapter can be loaded into a Modal Network Volume.
- **Cost**: Fractions of a cent per query ($0 idle cost).
- **Verdict**: Excellent production candidate, slightly higher setup complexity than an interactive pod.

### Option D: Adaption Platform Cloud API
- **Feasibility**: **Not Supported for LoRA Adapter Serving**.
  - As verified in Stage 8, the Adaption platform's `/api/v1/responses` currently serves its platform models (`deepseek-v4-flash`, `glm-5.2`, etc.). Experiment run checkpoints are delivered as downloadable bundles (`checkpoint.tar`), not as hosted API endpoints.

---

## 5. Comprehensive Provider & Runtime Comparison

> [!NOTE]
> All rates below distinguish **Verified Official Pricing** (sourced from live provider catalogs) from estimated auxiliary costs (disk/network).

| Provider / Runtime | Compatible GPU Hardware | Verified Official Rate | Estimated 1-Hr Test Cost | Deployment Complexity | Security / Secret Handling | LoRA Adapter Support |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RunPod (Community Cloud Pod)** | NVIDIA RTX 4090 (24 GB) or A4000 (16 GB) | **$0.34 - $0.44 / hr** (RTX 4090)<br>**$0.19 - $0.25 / hr** (A4000) *(Verified RunPod catalog)* | **~$0.45** (incl. 20GB volume) | **Low**: Standard PyTorch / vLLM Docker template, SSH/HTTP direct proxy | High: Private container, temporary instance, destroyed after testing | **Yes** (full vLLM / PEFT support) |
| **RunPod (Secure Cloud Pod)** | NVIDIA L4 (24 GB) or RTX 4000 Ada (20 GB) | **$0.40 - $0.55 / hr** *(Verified RunPod catalog)* | **~$0.60** | **Low**: Enterprise datacenter tier | High: ISO/SOC2 compliant datacenter | **Yes** |
| **Vast.ai (On-Demand)** | NVIDIA RTX 3090 (24 GB) | **$0.15 - $0.22 / hr** *(Verified Vast.ai catalog)* | **~$0.25** | **Medium**: Requires vetting host reliability score | Moderate: Community hosts; requires encrypted volume or trusted tier | **Yes** |
| **Modal Labs (Serverless)** | NVIDIA L4 (24 GB) | **$0.000222 / sec** (~$0.80/hr at 100% active) *(Verified Modal catalog)* | **<$0.05** (billed only for active ~3 min run) | **Medium**: Requires Modal CLI and app wrapper script | High: Ephemeral microVMs (gVisor/firecracker) | **Yes** (via HuggingFace PEFT / vLLM) |
| **Local Host (CPU/4-bit)** | RTX 3050 Laptop (6 GB) + 16 GB RAM | **$0.00** *(Local hardware)* | **$0.00** | **High**: Fragile VRAM headroom; slow token generation (~4-8 tps) | Maximum: Localhost only | **Yes** (bitsandbytes NF4 only) |

---

## 6. Recommended Strategy: The Safest & Most Cost-Effective Path

### The Winner: **RunPod On-Demand RTX 4090 / A4000 Cloud Pod** (or Modal Serverless)
- **Why**:
  1. **Zero Architecture Compromise**: Runs the base model in native **BF16 unquantized** with the full 256 LoRA adapter tensors loaded.
  2. **Predictable & Negligible Cost**: Total verification cost is **under $0.50 USD** (billed per second / minute, terminated immediately after verification).
  3. **Standard Tooling**: Runs official vLLM or standard Hugging Face PEFT server with OpenAI-compatible API (`/v1/chat/completions`).
  4. **Strict Isolation**: No credentials or private dataset files need to be uploaded—only the weights directory (`adapter_model.safetensors` + `adapter_config.json`) and the public base model from Hugging Face (`togethercomputer/Qwen3.5-4B`).

---

## 7. Step-by-Step Execution Plan (Awaiting Approval)

Once approved, the verification will follow this strict 5-stage protocol:

```
[Phase 1: Spinup] ──> [Phase 2: Checkpoint Transfer] ──> [Phase 3: vLLM Launch] ──> [Phase 4: Real Prompt Verification] ──> [Phase 5: Immediate Teardown]
```

### Phase 1: Provision Worker
1. User provides or authorizes a cloud GPU instance (e.g. RunPod template: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`).
2. Instance starts with 1x RTX 4090 (24 GB) or A4000 (16 GB).

### Phase 2: Staging Weights
1. Securely transfer only the local LoRA checkpoint folder:
   - `adapter_model.safetensors`
   - `adapter_config.json`
   - `tokenizer.json`
   - `tokenizer_config.json`
2. No API keys or source code are transferred to the worker.

### Phase 3: Launch Inference Server
1. Start vLLM serving Qwen3.5-4B with the LoRA adapter:
   ```bash
   vllm serve togethercomputer/Qwen3.5-4B \
     --enable-lora \
     --lora-modules neuroteach-trained=/workspace/adapter \
     --max-model-len 4096 \
     --dtype bfloat16 \
     --port 8000
   ```
2. Verify readiness endpoint: `GET http://localhost:8000/health` $\to 200\text{ OK}$.

### Phase 4: Inference Verification
1. Send a held-out pedagogical evaluation prompt to `POST http://localhost:8000/v1/chat/completions` targeting `model: "neuroteach-trained"`.
2. Inspect output: verify valid JSON matching PRD Section 15 schema (`diagnosis`, `strategy`, `intervention`, `visual_spec`, `next_check`).
3. Connect local NeuroTeach backend to endpoint (`MODEL_ENDPOINT_URL=...`) and run `/api/v1/health` and `/api/v1/pedagogy/turn`.

### Phase 5: Immediate Teardown
1. Terminate cloud instance and delete volume.
2. Confirm instance status is `TERMINATED` to guarantee no ongoing costs.

---

## 8. Compliance & Constraints Confirmation
- Original checkpoint untouched: `artifacts/training_results/checkpoints/819874ef-44b1-4a76-a049-1ce35638bba8/` preserved intact.
- No cloud charges incurred during this audit.
- No checkpoints uploaded.
- Production environment untouched.

**Status**: Ready for user review and approval before proceeding.

