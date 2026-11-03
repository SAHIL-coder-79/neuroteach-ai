# Requirements Traceability Matrix — NEUROTEACH AI

This matrix links every Functional Requirement (FR), User Story (US), and Non-Functional Requirement (NFR) from the PRD to its specific module, priority, acceptance criteria, and verification methodology.

## 1. Functional Requirements Matrix

| Req ID | PRD Ref | Priority | Requirement Summary | Implementation Module | Acceptance Criteria | Verification Method |
|---|---|---|---|---|---|---|
| **REQ-AUTH-01** | FR-01, US-01 | P0 (MVP) | User registration, authentication, and session state persistence | `backend/modules/auth` | User signs up, logs in, receives JWT in HTTP-only cookie, persists profile across browser sessions | Integration test + Cypress/Playwright auth flow |
| **REQ-MDNA-01** | FR-03, US-02, US-03, Sec 9.1 | P0 (MVP) | Misconception DNA error classification (`careless`, `conceptual`, `unclear`) | `backend/modules/misconceptions` | Categorizes errors with confidence; conceptual requires confidence $\ge 0.6$ + rule signal; returns diagnosis card | Held-out benchmark test + Unit tests |
| **REQ-MDNA-02** | Sec 9.1, FR-03 | P0 (MVP) | Learner Misconception Profile state machine (`active`, `improving`, `resolved`, `regressed`) | `backend/modules/misconceptions` | State transitions strictly follow rule matrix: 2 consecutive correct moves active to improving; 3 across 2 sessions (including transfer) resolves | State machine unit tests |
| **REQ-MDNA-03** | Sec 9.1, FR-12 | P0 (MVP) | Prerequisite linking & remediation trigger | `backend/modules/misconceptions` + `content` | If same misconception recurs after 2 interventions, Roadmap inserts prerequisite check on root concept | End-to-end learning flow test |
| **REQ-POL-01** | FR-04, US-05, Sec 9.2 | P0 (MVP) | 8-Strategy Adaptive Teaching Policy Engine | `backend/modules/policy` | Dynamically selects from the 8 strategies; records choice, rationale, and outcome | Policy unit tests & intervention log audit |
| **REQ-POL-02** | FR-05, US-04, Sec 9.2 | P0 (MVP) | Deterministic Answer Leakage Guardrail | `backend/modules/policy` | 0% of displayed hints contain final answer or trivial paraphrase before hint ladder level 3 is exhausted | Leakage detector test suite on 100% test items |
| **REQ-POL-03** | Sec 9.2 | P0 (MVP) | Strategy Switching & Fading Logic | `backend/modules/policy` | After 2 consecutive failures for same misconception, strategy switches; faded support on correct step | Policy transition unit test |
| **REQ-TP-01** | FR-06, US-06, Sec 9.3 | P0 (MVP) | TransferProof Multi-Level Assessment Generation | `backend/modules/transfer` | Issues unseen transfer items (Near=0.5, Medium=0.8, Far=1.0) with text similarity $< 0.8$ against taught example | Cosine similarity & parameter check test |
| **REQ-TP-02** | FR-07, US-07, Sec 9.3 | P0 (MVP) | Explainable Bayesian Smoothed Mastery Formula | `backend/modules/transfer` | Computes $M = \frac{1 + \sum w_i c_i}{2 + \sum w_i}$; requires $M \ge 0.80$, 3 items, 2 sessions, 0 active misconceptions for mastery | Unit tests with mathematical edge cases |
| **REQ-VPL-01** | FR-08, US-08, Sec 10.1, 10.2 | P0 (MVP) | Typed Visual Specification (Schema v1) | `backend/modules/visual` | Outputs strict JSON spec for `function_plot`, `coordinate_geometry`, `data_chart`, `tree` (BST) | Pydantic validation suite |
| **REQ-VPL-02** | FR-09, Sec 10.3 | P0 (MVP) | Deterministic Validation Pipeline (7 Steps) | `backend/modules/visual` | SymPy AST whitelist, 200-pt domain sampling, feature recomputation ($\le 10^{-3}$ numeric diff), distractor check | Automated pipeline test with 100 corrupted specs |
| **REQ-VPL-03** | FR-10, US-09, US-10, Sec 10.4 | P0 (MVP) | Generate Similar Question & Change Pattern | `backend/modules/visual` | Generates verified question under 3s (90th percentile) with 0 duplicates across 50 consecutive calls | Benchmark script & collision test |
| **REQ-VPL-04** | US-11, Sec 10.5 | P0 (MVP) | Client-side Interactive Parameter Sliders | `frontend/visual-lab` | Sliders update curves & derived points in $< 200\text{ ms}$ client-side via JSXGraph | Client performance profiling |
| **REQ-CONT-01** | FR-02, FR-12, Sec 8.3 | P0 (MVP) | Pre-seeded Concept Graph & Question Bank | `backend/modules/content` | Pre-loaded with $\ge 25$ concepts across 4 subjects and $\ge 60$ validated questions | Seed migration check |
| **REQ-UI-01** | FR-11, US-12, Sec 8.1 | P0 (MVP) | Home Dashboard View | `frontend/pages/Home` | Renders daily goal ring, streak counter, weak concepts list, and top 3 recommended activities | UI component tests |
| **REQ-UI-02** | Sec 8.2, S3 | P0 (MVP) | Ask Neuro Conversational Interface | `frontend/pages/AskNeuro` | Structured dialogue turns, diagnosis card, hint ladder, visual panel, and insight sidebar | UI integration test |
| **REQ-UI-03** | Sec 8.4, S5 | P0 (MVP) | Practice Arena & Question View | `frontend/pages/Practice` | Displays question, optional visual canvas, reasoning box, hint action, Similar Question button | UI integration test |
| **REQ-UI-04** | FR-12, Sec 8.3, S6 | P0 (MVP) | Roadmap & Prerequisite Visualizer | `frontend/pages/Roadmap` | Visualizes node states (locked, available, in-progress, mastered) and prerequisite links | Graph rendering test |
| **REQ-UI-05** | FR-13, US-14, Sec 8.12, S8 | P0 (MVP) | Evaluator & Mastery Evidence Breakdown | `frontend/pages/Evaluator` | Displays mastery scores, misconception report, evidence weights, and TransferProof status | UI component test |
| **REQ-EVAL-01** | FR-17, Sec 17 | P0 (MVP) | Single-Command Automated Benchmark Harness | `backend/modules/eval` + `ml/evaluations` | Single command runs B0, B1, and NT on held-out tasks and outputs metric report with confidence intervals | Benchmark harness test |
| **REQ-OBS-01** | FR-18, Sec 14 | P0 (MVP) | Structured Logging & Model Observability | `backend/app/observability` | Logs input hash, output, latency, token count, and validator verdicts to `model_calls` without PII | Log assertion test |

---

## 2. Non-Functional Requirements (NFR)

| NFR ID | Area | Specification | Acceptance Criteria |
|---|---|---|---|
| **NFR-PERF-01** | Latency | Visual generation & validation | Similar Question generation completed in $< 3.0\text{s}$ (90th percentile) |
| **NFR-PERF-02** | Responsiveness | Graph slider updates | Real-time curve updates in $< 200\text{ms}$ client-side |
| **NFR-SEC-01** | Input Validation | Math expression parser | Strictly whitelist SymPy symbols and operations; 0 `eval()` usage |
| **NFR-SEC-02** | Privacy | PII & Free-text protection | No student reasoning text stored in application trace logs |
| **NFR-A11Y-01** | Accessibility | WCAG Compliance | Dark-mode palette meets WCAG 2.2 AA contrast; text alternatives for all visuals |
| **NFR-REL-01** | Resilience | Fallback on Model Failure | 100% of failed model outputs fallback gracefully to verified static hints |

---

## 3. Phase 2 & Phase 3 (Future Scope) Traceability

| Req ID | Module | Phase | Description |
|---|---|---|---|
| **FUT-01** | Sessions History | Phase 2 | Full historical revision and transcript search |
| **FUT-02** | Roleplay | Phase 2 | Mock technical interviews and viva practice |
| **FUT-03** | Workshop | Phase 2 | Step-by-step interactive guided lessons |
| **FUT-04** | Scenarios | Phase 2 | Branching case-study decision questions |
| **FUT-05** | Library | Phase 2 | PDF document upload, chunking, and RAG search |
| **FUT-06** | Flopod | Phase 3 | Text-to-speech audio topic revision summaries |
| **FUT-07** | Mind Map | Phase 2 | Dynamic 100-node zoomable concept map via React Flow |
