# NEUROTEACH AI — URGENT 4-HOUR COMPLETION PLAN

**Audit & Plan Date**: 2026-11-03  
**Time Remaining**: ~4 to 4.5 Hours  
**Hard Constraints**:
- Zero paid cloud resources (no RunPod, no Modal, no Vast.ai, no GPU rentals).
- No new features, no full rewrites, no re-training.
- Verified LoRA checkpoint preserved intact.
- Deterministic and rule-based pedagogical modules celebrated honestly without fabricating LLM outputs.
- Deliver a rock-solid, cohesive, high-polish end-to-end demo.

---

## 1. Rapid Project Audit

### 1.1 Frontend Feature Audit
| Module / View | Current State | Working Genuinely? | Findings & Issues |
| :--- | :--- | :--- | :--- |
| **Home Dashboard** (`HomePage.tsx`) | Complete UI | **Yes (UI only)** | Visual layout, streak tracker, priority recommendation cards, and weak concept widgets render beautifully. Links navigate to sub-pages. |
| **Interactive Tutor** (`AskNeuroPage.tsx`) | Rich Chat Stream | **Isolated Mock** | Renders student dialogue turns and diagnosis cards. Uses simulated client-side timeouts. **Not connected to backend `/api/v1/pedagogy/turn`**. |
| **Practice & Visual Lab** (`PracticePage.tsx`) | Interactive UI | **Partially Connected** | Correctness checking works locally. "Generate Similar" has hardcoded demo logic. **Needs connection to backend solver `/api/v1/pedagogy/visual/similar-question`**. |
| **Curriculum Roadmap** (`RoadmapPage.tsx`) | Complete UI | **Yes** | Subject filters (Mathematics, Python, DSA, AI/ML) work cleanly. Concept nodes with prerequisite badges render accurately. |
| **Evaluator & Mastery** (`EvaluatorPage.tsx`) | Complete UI | **Yes** | Displays Bayesian Mastery Formula, Misconception DNA ledger, and TransferProof benchmark comparison. |
| **Interactive Graph Panel** (`GraphPanel.tsx`) | SVG Canvas | **Yes** | Real-time interactive curvature slider ($a$), vertex coordinate plotting, and deterministic validation badge. |

### 1.2 Backend Endpoint Audit
| Endpoint | Method | Status | Backing Engine |
| :--- | :--- | :--- | :--- |
| `/api/v1/health` | GET | **Passing** | Database connection check + Model Provenance & Readiness reporting. |
| `/api/v1/pedagogy/turn` | POST | **Passing** | `PedagogicalModelClient` + `TeachingPolicyEngine` (leakage guardrail) + `MisconceptionDNAEngine`. Returns 503 if model offline and fallback disabled. |
| `/api/v1/pedagogy/visual/validate` | POST | **Passing** | Deterministic 7-step SymPy validation (`VisualSpecValidator`). |
| `/api/v1/pedagogy/visual/similar-question` | GET | **Passing** | Pattern-based generator (`PatternLibrary.generate_parabola_vertex_question`). |
| `/api/v1/pedagogy/evaluator/misconceptions` | GET | **Passing** | Returns full `MISCONCEPTION_CATALOG`. |

### 1.3 Pedagogical Features & Model Calling Analysis
1. **Misconception DNA Classification**:
   - Model Proposal (`confidence` estimate) is combined with deterministic consensus matching (`MisconceptionDNAEngine.classify_error`).
   - If model endpoint is offline, fallback simulator (`_simulate_fallback_turn`) provides valid diagnosis structure when fallback is enabled.
2. **Adaptive Teaching Strategy**:
   - Deterministic policy engine (`AdaptiveTeachingEngine.select_strategy`) selects `progressive_hint`, `counterexample`, or `simpler_prerequisite` based on student attempt history and past strategy failures.
3. **Answer Leakage Guardrail**:
   - 100% deterministic SymPy and regex token matching (`TeachingPolicyEngine.detect_answer_leakage`).
4. **TransferProof Verification**:
   - 100% deterministic evaluation of student attempts on held-out isomorphic and far-transfer items.

### 1.4 Adaption Platform Hosted Inference Audit
- **Audited SDK Resources**: `client.autoscientist`, `client.models`, `client.responses`, `client.training_models`.
- **Finding**: Adaption AutoScientist is an autonomous training engine that outputs exportable weights (`checkpoint.tar`). Its public inference API (`client.responses.create()`) serves platform foundation models (`deepseek-v4-flash`, `glm-5.2`, `qwen3.5-397b`), but **does not provide hosted endpoints for custom private LoRA adapters** (returns 404).
- **Honest Architectural Positioning**: We must celebrate this clearly. The LoRA adapter was genuinely fine-tuned and verified with an official 75.23% win rate. The backend is fully integrated to consume it via any OpenAI-compatible endpoint. For local/offline demo presentation, the backend cleanly orchestrates its deterministic pedagogical engines and documents the model readiness status truthfully.

---

## 2. P0 / P1 / P2 Prioritization Matrix

### P0: Essential for Winning Demo (Must Complete in 2 Hours)
- [x] **P0.1**: Verified Checkpoint & Provenance (Done in Stage 8).
- [ ] **P0.2**: Connect Frontend `AskNeuroPage` directly to Backend `/api/v1/pedagogy/turn`.
  - When student submits an attempt, send real JSON to backend.
  - Surface error diagnosis, strategy name, and progressive hints returned by the engine.
- [ ] **P0.3**: Connect Frontend `PracticePage` to `/api/v1/pedagogy/visual/similar-question`.
  - "Generate Similar Question" button fetches solver-verified dynamic questions from the backend.
- [ ] **P0.4**: Connect Subject Switching (Math, Python, DSA, AI/ML) to genuine demo problem sets.
- [ ] **P0.5**: End-to-End Demo Script & Documentation.

### P1: Important Polish (Complete in Hour 3)
- [ ] **P1.1**: Add a transparent "Inference Mode" badge in the UI (e.g. `Pedagogical Engine: Hybrid Deterministic Core | Adapter Checkpoint: 819874ef`).
- [ ] **P1.2**: Responsive visual bug fixes & empty state touch-ups.
- [ ] **P1.3**: Automated startup script (`start_demo.bat` or `start_demo.sh`) that spins up backend (Uvicorn) and frontend (Vite) simultaneously.

### P2: Postponed / Not in 4-Hour Scope
- ❌ Re-architecting database schemas or adding complex OAuth authentication.
- ❌ Local 4-bit CUDA compilation or paid cloud worker deployment.
- ❌ Building unrequested curriculum subjects beyond the 4 core subjects.

---

## 3. Four-Hour Sprint Execution Checklist

```
[Hour 1: API Bridge] ──> [Hour 2: Visual Lab & Subjects] ──> [Hour 3: Polish & Startup] ──> [Hour 4: Docs & Dry Run]
```

### Hour 1: Connect Frontend to Real Backend API
- Create a lightweight API client `frontend/src/api/pedagogy.ts`.
- Wire `AskNeuroPage.tsx` to `POST /api/v1/pedagogy/turn`.
- Wire `PracticePage.tsx` to `GET /api/v1/pedagogy/visual/similar-question`.
- Ensure graceful error states and loading spinners.

### Hour 2: Complete Full Student Journey Across 4 Subjects
- Support switching between Mathematics (Parabola Vertex), Python (Loop Off-by-one), DSA (Binary Search Bounds), and AI/ML (Gradient Step).
- Ensure student can submit attempt $\to$ receive diagnosis $\to$ receive hint $\to$ solve transfer question.
- Verify SVG Canvas rendering for visual problems.

### Hour 3: UI Polishing & System Health Indicator
- Display live health & model provenance widget (pulling from `GET /api/v1/health`).
- Ensure mobile/tablet responsive layouts on all screens.
- Build single-command demo launcher (`start_demo.bat`).

### Hour 4: Verification, Test Suites & Documentation
- Run `pytest backend/tests` (maintain 100% pass rate).
- Run `npm run build` (maintain 0 build errors).
- Generate:
  - `docs/FINAL_COMPLETION_REPORT.md`
  - `docs/FINAL_DEMO_SCRIPT.md`
  - `docs/KNOWN_LIMITATIONS.md`

---

## 4. Highest-Priority Next Actions (Starting Immediately)

1. **Step 1**: Create `frontend/src/api/client.ts` to connect React directly to FastAPI backend (`http://localhost:8000/api/v1`).
2. **Step 2**: Update `AskNeuroPage.tsx` to call `/api/v1/pedagogy/turn` for real pedagogical analysis.
3. **Step 3**: Update `PracticePage.tsx` to fetch generated similar questions dynamically from `/api/v1/pedagogy/visual/similar-question`.

