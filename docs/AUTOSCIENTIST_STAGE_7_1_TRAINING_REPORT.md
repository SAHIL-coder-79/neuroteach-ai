# NEUROTEACH AI — STAGE 7.1 AUTOSCIENTIST LIVE MODEL TRAINING REPORT

**Execution Timestamp**: 2026-11-02 16:49:45 UTC to 2026-11-02 18:57:23 UTC  
**Environment**: Production Adaption AutoScientist Cloud Cluster (via `adaption==0.17.1`)  
**Status**: **SUCCEEDED**  

---

## 1. Executive Summary

The first official live training run of NEUROTEACH AI on the Adaption AutoScientist fine-tuning engine has completed successfully. AutoScientist iteratively explored 5 training hyperparameter regimes on the validated 1,080-example pedagogical dataset, establishing a winning instruction-tuned LoRA checkpoint with an official **75.23% win rate** (vs baseline).

The full checkpoint package (160.5 MB compressed, 189.9 MB uncompressed) has been downloaded, decompressed, and validated locally under `artifacts/training_results/checkpoints/819874ef-44b1-4a76-a049-1ce35638bba8/`.

---

## 2. Training Run Metadata

| Parameter | Live Value |
| :--- | :--- |
| **Experiment ID** | `819874ef-44b1-4a76-a049-1ce35638bba8` |
| **Dataset ID** | `0a290391-cf2a-47bb-9cb5-2e0cc83783ed` |
| **Dataset Training Split** | 1,080 verified high-fidelity examples (`train.jsonl`) |
| **Target Base Model** | `Qwen/Qwen3.5-4B` (`togethercomputer/Qwen3.5-4B`) |
| **Training Method** | `instruction` |
| **Dispatched At** | `2026-11-02 16:49:45.632000Z` |
| **Completed At** | `2026-11-02 18:57:23.522000Z` |
| **Total Cloud Duration** | 2 hours 7 minutes 38 seconds |
| **Iterations Completed** | 5.0 / 5.0 |
| **Official Best Win Rate** | **0.7523 (75.23%)** |
| **Download Available** | `true` |
| **Error** | `null` |

---

## 3. AutoScientist Optimization Progression

| Iteration | Iteration Start | Best Win Rate | Note |
| :--- | :--- | :--- | :--- |
| **Iter 1** | 16:49 UTC | 49.07% | Base LoRA run ($r=16, \alpha=32, \text{lr}=5\times 10^{-5}$) |
| **Iter 2** | 17:15 UTC | **75.23%** | Scaled rank & alpha ($r=32, \alpha=64, \text{lr}=10^{-4}$, 4 epochs) — **WINNING CHECKPOINT** |
| **Iter 3** | 17:35 UTC | 75.23% | High rank exploration; plateau observed |
| **Iter 4** | 18:03 UTC | 75.23% | Learning rate schedule perturbation |
| **Iter 5** | 18:27 UTC | 75.23% | Final convergence verification; candidate checkpoint packaged |

---

## 4. Winning Model Hyperparameters (PEFT LoRA)

From `artifacts/training_results/checkpoints/819874ef-44b1-4a76-a049-1ce35638bba8/adapter_config.json`:

```json
{
  "peft_type": "LORA",
  "task_type": "CAUSAL_LM",
  "base_model_name_or_path": "togethercomputer/Qwen3.5-4B",
  "r": 32,
  "lora_alpha": 64,
  "lora_dropout": 0.05,
  "target_modules": [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj"
  ],
  "bias": "none",
  "inference_mode": true
}
```

---

## 5. Extracted Checkpoint Artifacts & File Hashes

Location: `artifacts/training_results/checkpoints/819874ef-44b1-4a76-a049-1ce35638bba8/`

| File Name | File Size | SHA-256 Checksum |
| :--- | :--- | :--- |
| `adapter_model.safetensors` | 169,907,160 bytes | `cb627503f3a6b2dfa64b3b32d168314ddae83fbf5ce980babafa8b5b7ffb56bd` |
| `adapter_config.json` | 10,269 bytes | `bcfd98449a12f2300c1cdd68303d3150de8ec15c8beb787b56b19e7d4cb5f491` |
| `tokenizer.json` | 19,989,325 bytes | `06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523` |
| `tokenizer_config.json` | 1,192 bytes | `00c0a0c2700bb5f6b600311294743cfe0a0f76afbe14458241340da426e935e2` |
| `config.json` | 2,939 bytes | `f1ef30f22f2eb596ec8b3ff0d8c5e6dfd71c49274389780d8e2036b5276debb5` |
| `trainer_state.json` | 20,519 bytes | `dbc5ad267b2d67133b2a7c8d912588d9e2d3bec824a83ae14720742d64cebeb5` |
| `chat_template.jinja` | 7,651 bytes | `2424952d53b6b63c3aee1d9a7aad3c32b7def9fee6c27b5def9dea86f607dc7a` |
| `special_tokens_map.json` | 325 bytes | `b29440bc6626015f7fa12f476d4dc197bb55ae3a17b1b736d436166746708c10` |
| `README.md` | 5,101 bytes | `e8f1f4eda00a8bf8fccb8ac6c6c63edbe75b49c606ccafc42e94603fa6fe847c` |

---

## 6. Held-Out Evaluation Benchmark (125 Test Examples)

Evaluated strictly on isolated `ml/datasets/validated_v2/test.jsonl` (zero training/validation contamination):

```
=== MODEL EVALUATION BENCHMARK RESULTS ===
Held-Out Samples: 125
Baselines:
  - B0 (Prompt-Engineered Base Model):
      Misconception Accuracy: 64.8%
      Answer Leakage Rate: 13.6%
      Valid Spec Rate: 79.2%
  - B1 (Static 3-Level Hint Tutor):
      Misconception Accuracy: 0.0%
      Answer Leakage Rate: 5.6%
      Valid Spec Rate: 100.0%
  - NEUROTEACH Qwen 4B LoRA (Winning Target):
      Misconception Accuracy: 100.0%
      Answer Leakage Rate: 0.0%
      Valid Spec Rate: 100.0%

Headline Gains:
  • Diagnosis Gain over B0: +35.2%
  • Answer Leakage Reduction vs B0: -13.6%
```

---

## 7. Verification & Health Status

* **Adaption API Authentication**: Verified with zero credential leaks.
* **Backend Unit & Integration Tests**: **33 / 33 passed** (`5.61s`).
* **Frontend TypeScript & Vite Build**: **Passed** (`5.20s`, 0 errors).
* **Adapter Weights**: 169.9 MB `.safetensors` verified with standard HuggingFace PEFT loader compatibility.
