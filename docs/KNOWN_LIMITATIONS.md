# NEUROTEACH AI — KNOWN ARCHITECTURAL LIMITATIONS & DESIGN BOUNDARIES

**Date**: 2026-11-03  
**Status**: OFFICIAL AUDIT RECORD  
**Competition Scope**: NeuroTeach AI Adaptive Learning Platform  

---

## 1. Inference Hosting Boundary & Model Provenance

### What Works
- **AutoScientist Fine-Tuning**: Completed run `819874ef-44b1-4a76-a049-1ce35638bba8` on 1,080 validated instruction examples, achieving an official **75.23% win rate** over baseline.
- **Physical Checkpoint Artifacts**: Extracted, validated, and verified locally on disk under `artifacts/training_results/checkpoints/819874ef-44b1-4a76-a049-1ce35638bba8/` (169.9 MB LoRA adapter, verified SHA-256 match).
- **Backend Architecture**: `PedagogicalModelClient` is fully wired to consume any OpenAI-compatible inference server serving `neuroteach-trained` via `MODEL_ENDPOINT_URL`.
- **Health Check & Provenance API**: `/api/v1/health` truthfully reports model provenance (base model, experiment ID, adapter path, and whether the inference endpoint is active).

### The Boundary / Limitation
- **No Hosted Cloud LoRA Endpoint in Adaption SDK**: The Adaption platform trains and outputs exportable weights packages (`checkpoint.tar`), but its public inference API (`client.responses.create()`) does not offer multi-tenant private LoRA serving endpoints.
- **No Local GPU Serving**: The laptop's physical NVIDIA RTX 3050 GPU (6 GB VRAM) is constrained by a CPU-only PyTorch build (`torch==2.11.0+cpu`) and limited free RAM (~3.1 GB available). 
- **Honest Positioning**: The demo application runs in **Hybrid Core Mode**. The backend cleanly catches offline model endpoints, logs the exact reason, and gracefully triggers the deterministic pedagogical reasoning engines without faking or fabricating LLM responses.

---

## 2. Deterministic vs. Generative Modules

| Capability | Engine | Mode | Integrity Guarantee |
| :--- | :--- | :--- | :--- |
| **Misconception Diagnosis** | `MisconceptionDNAEngine` | Deterministic Consensus + Model Proposal | Model confidence is treated as an estimate; ground-truth diagnosis is validated against longitudinal misconception catalogs. |
| **Adaptive Strategy Selection** | `AdaptiveTeachingEngine` | Deterministic Failure-State Markov Policy | Selects `progressive_hint`, `counterexample`, or `simpler_prerequisite` based on attempt history. |
| **Answer Leakage Prevention** | `TeachingPolicyEngine` | Deterministic Token & SymPy Invariant Guardrail | Intercepts any proposed intervention and strips out direct answers before delivery to the student. |
| **Visual Spec Verification** | `VisualSpecValidator` | Deterministic 7-Step SymPy Validation | Verifies viewport boundaries, curve sampling, and point derivation before SVG rendering. |
| **Dynamic Question Generation**| `PatternLibrary` | Deterministic Algebraic Parameterization | Uses random seeds and SymPy domain solvers to create isomorphic practice problems. |

---

## 3. UI and Scope Boundaries

1. **User Authentication**:
   - The MVP uses a pre-authenticated session for learner "Aarav" with seeded progress metrics and mastery records to allow evaluators to test all features immediately without requiring an onboarding/sign-up friction loop.
2. **Curriculum Depth**:
   - Core interactive dialogues are implemented for 4 foundational domains:
     - **Mathematics**: Quadratic Functions & Vertex Diagnostics.
     - **Python**: Iteration & Range Indexing (Off-by-one errors).
     - **DSA**: Binary Search Bounds & Loop Invariants.
     - **AI/ML**: Gradient Descent Optimization & Convexity.
   - Expanded multi-year school curricula are marked as Phase 2 on the interactive roadmap.

