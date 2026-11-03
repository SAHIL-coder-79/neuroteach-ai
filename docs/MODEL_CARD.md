# Model Card: NEUROTEACH AI Fine-Tuned Pedagogical Model

## 1. Model Details
- **Model Name**: NEUROTEACH-Tutor-v1
- **Model Architecture**: Instruction-tuned open model (~7B–8B base, e.g., Llama-3.1/3.3 or Mixtral via LoRA adapter)
- **Training Platform**: Adaption AutoScientist (Adaptive Data co-optimization & LoRA recipe)
- **Language**: English
- **Domain**: Computer Science, Information Technology, and Mathematics (Python, DSA, AI/ML, Engineering Math)
- **Task**: Multi-task instructional dialogue for tutoring (Misconception Diagnosis, Teaching Strategy Selection, Guardrailed Non-leaking Interventions, Visual Spec Synthesis, Similar Question Generation)

## 2. Intended Use & Capabilities
The model powers NEUROTEACH AI's conversational and practice engine. Its multi-task capabilities include:
1. **Misconception Diagnosis**: Classifies student errors into `careless`, `conceptual`, or `unclear`, mapping conceptual errors to an authoritative misconception catalog.
2. **Pedagogical Strategy Selection**: Dynamically selects from 8 research-grounded teaching strategies (Progressive Hint, Step-by-Step, Example-based, Counterexample, Contrastive, Analogy, Simpler Prerequisite, Guided Problem Solving).
3. **Scaffolded Non-Leaking Interventions**: Generates hints without giving away the final numerical/symbolic answer.
4. **Structured Visual Specification**: Synthesizes verified JSON schemas (`visual_spec`) for mathematical plots, BST trees, and algorithmic structures.
5. **Contextual Question Generation**: Generates new question contexts around verified mathematical and algorithmic patterns.

## 3. Training Data & Strategy
- **Dataset Size**: 3,000–6,000 synthetic high-fidelity multi-turn teaching interactions.
- **Subjects**: Mathematics (Algebra, Calculus), DSA (Trees, Sorting, Searching), AI/ML (Linear Models, Gradients), Python (Loops, Slicing).
- **Data Construction Pipeline**:
  - Authoritative catalog of ~60 curated misconceptions with formal rules.
  - Template solvers generating deterministic correct and distractor values.
  - Student simulator with varied voice, careless slips, and false conceptual rules.
  - Teacher LLM generation constrained by strategy and catalog entry.
  - Automatic validation: SymPy solver check, answer leakage detector, and cross-family LLM judge.
- **Leakage Prevention**: Strictly stratified splits (Test set holds out 15% unseen misconceptions, 20% unseen templates, and full topics before training).

## 4. Evaluation & Benchmark Performance
Compared against B0 (Base prompt-engineered model) and B1 (Static 3-level hint tutor):
- **Misconception Diagnosis Accuracy**: NT targets $\ge 15\%$ gain over B0.
- **Answer Leakage Rate**: $\le 2\%$ on hint interventions (enforced by deterministic backend guards).
- **Strategy Selection Alignment**: Matches pedagogical decision-matrix targets.
- **Visual Spec Validity**: 100% shown pass rate (via backend deterministic validation pipeline).

## 5. Guardrails & Safety
- **No Free Drawing**: The model only generates typed JSON specs, verified via SymPy domain sampling.
- **Answer Leakage Check**: Automated regex and embedding filter drops any intervention that leaks the answer before level 3 hints are exhausted.
- **Strategy Switching**: Deterministic state machine enforces strategy changes when a method fails twice.

## 6. Adaption AutoScientist Programmatic Integration
The programmatic training and orchestration pipeline connects directly to Adaption AutoScientist:
- **SDK Version Verified**: `adaption==0.17.1` (installed and verified in backend Python 3.10 virtual environment)
- **Official Documentation**: `https://docs.adaptionlabs.ai/autoscientist-quickstart/`
- **Integration Layer**: `backend/app/modules/autoscientist/service.py` (`AutoScientistService`)
- **CLI Runner**: `ml/scripts/autoscientist_runner.py`
- **Security & Key Management**:
  - `ADAPTION_API_KEY` is loaded exclusively from backend environment variables (`backend/app/core/config.py`).
  - Never exposed to frontend / browser code.
  - Automatically redacted from retry and debug log messages.
- **Safety Boundary & Paid Operation Gate**:
  - Safe Dry-Run mode is strictly preserved as the default (`ADAPTION_DRY_RUN=True`).
  - No cloud training run or paid operation is ever dispatched automatically.
  - `create_training_run` enforces a hard assertion requiring `user_confirmed_paid_operation=True` in live mode, or raises `PermissionError`.
  - All dry-run and mock outputs are explicitly tagged with `is_mock=True` to eliminate fabricated claims of cloud completion.
- **Verified 1:1 SDK Methods & Return Types**:
  - **Dataset Upload**: `client.datasets.upload_file(path, name=..., processing_mode="raw", column_mapping={"prompt": "prompt", "completion": "completion"})` -> `UploadCompleteByIDResponse(dataset_id, status)`
  - **Processing Status**: `client.datasets.get_status(dataset_id=...)` -> `DatasetGetStatusResponse(dataset_id, status, row_count, progress, error_data)`
  - **Model Listing**: `client.autoscientist.list_models()` -> `AutoscientistListModelsResponse(models=[Model(id, display_name, ...)])`
  - **Hyperparameter Recommendation**: `client.autoscientist.recommend_hyperparams(dataset_id=..., model=...)` -> `AutoscientistRecommendHyperparamsResponse(model, hyperparams)`
  - **Training Run Creation**: `client.autoscientist.create(dataset_id=..., model=..., training_method=..., ...)` -> `AutoscientistRun(id, dataset_id, status, ...)`
  - **Run Status Monitoring**: `client.autoscientist.get(experiment_id=...)` -> `AutoscientistRun`
  - **Best Checkpoint Download**: `client.autoscientist.download(experiment_id=...)` -> `BinaryAPIResponse.write_to_file(path)`


