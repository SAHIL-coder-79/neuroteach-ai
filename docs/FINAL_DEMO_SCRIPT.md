# NEUROTEACH AI — OFFICIAL EVALUATOR DEMO SCRIPT

**Walkthrough Duration**: 5 to 7 Minutes  
**Target Audience**: Competition Judges & Technical Evaluators  
**System URL**: `http://localhost:5173` (Frontend) | `http://localhost:8000` (Backend API)  

---

## 1. Quick Launch

Double-click `start_demo.bat` at the repository root. This opens:
- FastAPI Backend on `http://localhost:8000`
- React Vite Frontend on `http://localhost:5173`

Verify backend status at: `http://localhost:8000/api/v1/health`  
Notice the transparent `model_provenance` block displaying:
- Model Name: `neuroteach-trained`
- Base Model: `togethercomputer/Qwen3.5-4B`
- Adapter Experiment ID: `819874ef-44b1-4a76-a049-1ce35638bba8`
- Adapter Verified on Disk: `true`

---

## 2. Step 1: The Home Dashboard (`/home`)

1. Open `http://localhost:5173`.
2. Point out:
   - **Student Profile**: "Aarav" (Personalized daily goal progress ring: 2 of 3 concepts, 67% complete).
   - **Prioritized Recommendations Engine**: Recommends high-priority interventions based on active misconceptions and overdue transfer tests.
   - **Active Misconception Alert**: Highlights `sign_error_vertex` in Mathematics.
3. Click **"Review Misconception"** or navigate to **Ask Neuro** on the sidebar.

---

## 3. Step 2: The Socratic Tutor & Misconception Diagnostics (`/ask_neuro`)

1. **Student Question Context**:
   - The dialogue begins with the student's question:  
     *"I calculated the vertex for $f(x) = x^2 - 4x + 3$ and got $x = -2$, but the answer key says $x = 2$. Why am I wrong?"*
   - Student Reasoning: *"I used $x = b / (2a)$. Here $a=1$ and $b=-4$, so $-4 / 2 = -2$."*
2. **AI Diagnosis & Socratic Response**:
   - Point out the **Misconception Diagnosis Card**:
     - Error Type: **Conceptual**
     - Misconception: `sign_error_vertex` (Neglecting negative sign in $x = -b / (2a)$)
     - Confidence: **0.88**
     - Strategy: **Counterexample / Progressive Hint**
3. **Interactive Dialogue Test**:
   - In the chat input, type:  
     *"Wait, does the minus sign apply to the whole fraction or just b?"*
   - Click **Send**.
   - Notice the live backend processing indicator (`Analyzing Pedagogy...`). The backend `pedagogy/turn` route processes the input and returns a guided intervention that never leaks the final answer.
4. **Stuck / Prerequisite Fallback**:
   - Click **"I'm Stuck"**.
   - The adaptive engine steps down the hint ladder to a simpler prerequisite:  
     *"Let's step back to a simpler prerequisite: If you have $-(-4)$, what is that equal to?"*

---

## 4. Step 3: Practice & The Visual Pattern Lab (`/practice`)

1. Navigate to **Practice** in the sidebar.
2. Observe the **Interactive Visual Spec Panel**:
   - Interactive SVG canvas rendering the quadratic function $f(x) = x^2 - 4x + 3$.
   - Interactive **Curvature Parameter Slider ($a$)**: Drag the slider to observe how the parabola dynamically scales while maintaining the vertex invariant.
   - Notice the **"SymPy Solver Verified"** badge confirming mathematical correctness.
3. **Attempting the Problem**:
   - Enter `2` in the answer box and click **Submit Answer**.
   - A green **"Correct! You've mastered this step"** badge appears.
4. **Generating Dynamic Solver-Verified Similar Questions**:
   - Click **"Generate Similar Question"**.
   - The button queries `/api/v1/pedagogy/visual/similar-question` on the backend.
   - A new mathematically sound problem is dynamically generated ($f(x) = x^2 - 6x + 8$, canonical answer `3`), demonstrating transfer problem generation.

---

## 5. Step 4: Curriculum Learning Roadmap (`/roadmap`)

1. Navigate to **Roadmap** in the sidebar.
2. Select between the 4 core domains:
   - **Mathematics** (Standard Form $\to$ Vertex & Symmetry $\to$ Roots & Discriminants $\to$ Calculus Limits).
   - **Python** (Iteration & Range Indexing).
   - **DSA** (Binary Search Tree Insertion).
   - **AI/ML** (Gradient Descent Optimization).
3. Observe prerequisite graph enforcement: Mastered concepts show green checkmarks; advanced concepts remain locked until prerequisites are cleared.

---

## 6. Step 5: Explainable Evaluator & TransferProof (`/evaluator`)

1. Navigate to **Evaluator** in the sidebar.
2. Point out:
   - **Bayesian Mastery Formula Banner**: Explains how student mastery is smoothed ($M = \frac{\alpha_0 + \sum w_i c_i}{\alpha_0 + \beta_0 + \sum w_i}$) with transfer weights (Near = 0.5, Medium = 0.8, Far = 1.0).
   - **Misconception DNA Ledger**: Tracks historical occurrences, evidence counts, and resolution states across subjects.
   - **Benchmark Comparison Table**: Compares Base Model (B0), Static Hint Tutor (B1), and NeuroTeach AI (NT) on Misconception Accuracy (+17% gain) and Answer Leakage (0% with deterministic guardrails).

---

## 7. Conclusion
Summarize the presentation:
*"NeuroTeach AI bridges machine learning fine-tuning with deterministic pedagogical guardrails. The AutoScientist LoRA model was successfully trained to 75.23% win rate and verified locally, while our deterministic backend guarantees zero answer leakage and solver-verified visual explanations."*

