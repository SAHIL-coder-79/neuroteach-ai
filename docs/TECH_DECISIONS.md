# Technical Decisions & Architecture Decision Records (ADRs) — NEUROTEACH AI

## ADR-01: Monolith vs Microservices Architecture
- **Decision**: Adopt a **Modular Monolith** using FastAPI on the backend and React (Vite) on the frontend.
- **Context**: The competition window is constrained (~8 hours). Microservices introduce latency overhead, complex network topologies, multi-repo synchronization, and container orchestration overhead (Kubernetes).
- **Consequences**: Fast development velocity, atomic transactions across learner states and attempts, simplified CI/CD, and zero network hops between tutoring orchestration, policy guards, and validators.

---

## ADR-02: Deterministic Guardrails over Pure Generative Output
- **Decision**: Never rely on raw model generation for correctness, mathematical calculations, visual plots, or mastery scoring.
- **Context**: LLMs hallucinate calculations, leak answers prematurely, and generate malformed coordinate geometry.
- **Consequences**:
  - Model outputs structured JSON proposals.
  - Backend uses SymPy AST whitelisting and numerical sampling to recompute features.
  - Leakage detector and answer checks reject faulty hints before they reach the client.
  - If validation fails twice, system falls back to pre-authored static hints with a user notice.

---

## ADR-03: Visual Rendering Technology Stack
- **Decision**:
  - **Interactive Math & Plots**: JSXGraph.
  - **Statistical / Data Charts**: Recharts.
  - **Trees & Algorithmic Graphs**: React Flow / Custom SVG.
- **Context**: General-purpose LLMs struggle with image generation and precise geometry. Typed JSON specs (`visual_spec` Schema v1) rendered client-side ensure sub-200ms interactive slider performance, SVG sharpness, and zero rendering hallucinations.

---

## ADR-04: Adaption AutoScientist Fine-Tuning Integration (Decisions D1–D4)
- **Base Model Selection (D1)**: Target open instruction-tuned 7B–8B model (e.g., Llama-3.1-8B or Mixtral-8x7B LoRA). Larger 70B models have latency unsuitable for a live multi-turn demo.
- **Hosted Inference vs Adapter Export (D2)**: Deploy adapter via hosted inference endpoint if provided by Adaption, with an async fallback to a local vLLM / Ollama instance for development and mock testing.
- **Dataset Splitting & Leakage Prevention (D3)**: Strictly hold out 15% of misconceptions and 20% of templates prior to training. Training augmentation (Adaptive Data) must never touch the frozen test set.
- **Confidence Calibration (D4)**: If token log-probabilities are unavailable over the inference API, calibrate confidence scores using temperature scaling against the held-out validation set.

---

## ADR-05: State Management & Database Strategy
- **Decision**: PostgreSQL with SQLAlchemy 2.0 (asyncio) + Pydantic v2.
- **Context**: Mastery tracking, attempts history, and session progression require relational consistency and foreign keys connecting attempts to specific misconceptions and prerequisite nodes.
- **Consequences**: Prevents race conditions during simultaneous attempt logging; enables rich SQL queries for Evaluator metrics.

---

## ADR-06: Authentication & Security
- **Decision**: Argon2 password hashing + short-lived JWT access tokens (15-min) with HTTP-only, SameSite=Strict refresh cookies.
- **Context**: Simple, secure, zero external OAuth dependencies during MVP phase, fully compliant with OWASP standards.
