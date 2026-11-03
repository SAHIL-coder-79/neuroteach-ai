NEUROTEACH AI — Product Requirements Document
Nov 2, 2026 · @sahil
NEUROTEACH AI is an adaptive learning platform whose core asset is a fine-tuned teaching model that diagnoses why a student is wrong, picks a teaching intervention, and checks transfer on unseen problems. The competition MVP is judged on that model and on measurable benchmark results, so every other module is secondary to it.
1. Executive Summary
NEUROTEACH AI targets engineering, CS and IT students learning Python, DSA, AI/ML and Mathematics. It differs from a chatbot in four ways:
• Misconception DNA names the conceptual error behind a wrong answer and tracks it across sessions.
• Adaptive Teaching Engine selects one of eight strategies per turn, observes the reply, and switches strategy when it fails.
• TransferProof refuses to declare mastery from one correct answer; it tests with new values, contexts and structures.
• Visual Pattern Lab renders validated graphs and diagrams from a safe JSON schema and generates verified similar questions.
The model is fine-tuned on a purpose-built dataset using Adaption's AutoScientist platform (see assumptions) and compared against a base model and a static hint tutor. Synthetic-data results prove model behaviour, not learner outcomes; the PRD keeps those claims separate.
Assumptions requiring confirmation
#
Assumption
Status
A1
"AutoScientist" means Adaption's AutoScientist (launched 13 May 2026), which fine-tunes open models and co-optimizes data and training recipe. Public adapters made with it use LoRA on Llama and Mixtral bases.
Verified from public pages; confirm current access, credits and supported models in your account
A2
Preference optimization (DPO or similar) is available on the platform.
Unverified — treat as Stage 4 stretch only
A3
Fine-tuned weights or an inference endpoint can be called from our FastAPI backend.
Unverified — confirm export or hosted-inference option before design freeze
A4
Competition window is about eight hours of build time; Phase 1 is scoped to fit only if the dataset exists beforehand.
Confirm event rules and any pre-build allowance
A5
Flo101 is a navigation and layout reference only; no proprietary assets or code are reused.
Confirmed by brief
A6
Initial users are logged-in students on desktop browsers; mobile is responsive but not native.
Confirm
2. Product Vision
A learning companion that behaves like a good tutor: it asks what the student thinks, finds the faulty mental model, tries the smallest helpful intervention, and then proves the student can solve a different problem alone. Success is a student who needs fewer hints on the next unseen problem, not one who got a polished explanation.
3. Problem Statement
1. Learning tools mark answers right or wrong and miss the underlying misconception, so the same error recurs.
2. Chat tutors often reveal answers early or repeat the same explanation style when it fails.
3. "Mastery" is usually inferred from a single correct answer or from re-seeing the taught example.
4. Visual topics (functions, graphs, trees, sorting) are explained in text or with unvalidated, hallucinated plots.
5. Wrapper products inherit a general model's behaviour; none of the pedagogy is learned.
4. Goals and Non-Goals
Goal
Measure
G1. Train a teaching model that beats the base model and a static hint tutor on held-out tasks
Wins on misconception accuracy, strategy accuracy and leakage rate (section 17)
G2. Deliver the four signature features end to end in the MVP
Acceptance criteria in section 25 pass
G3. Every graph and generated question is deterministically validated before display
0 invalid specs shown in test suite
G4. Mastery is evidence-based and explainable
Score breakdown visible; never set by one answer
G5. Ship a polished dark-mode UI for the five MVP modules
Design review checklist (section 13)
Non-goal
Reason
Claiming real learning gains from synthetic data
Needs a learner study; see section 17
Building all 13 modules in the competition window
Only Home, Ask Neuro, Practice, Roadmap, Evaluator are MVP
Copying Flo101 branding, copy or code
A5
Arbitrary AI-drawn images
Graphs come from validated JSON specs only
Native mobile apps, LMS integrations, multi-tenant school admin
Out of initial scope
Microservices, Kubernetes
A modular monolith is enough
5. Target Audience and User Personas
Three personas drive MVP decisions; the exam-sprint persona is the primary design target.
Persona
Context
Pain point
What NEUROTEACH must do
Aarav, 2nd-year IT student
Studies DSA and Python for semester exams, 1–2 h per day
Memorizes solutions, fails when the question is rephrased
Detect the misconception, teach with hints, verify with a changed problem
Meera, final-year CS student
Preparing for technical interviews and vivas
Cannot tell which concepts are actually weak
Evaluator with concept-wise mastery and misconception report; Roleplay later
Rohan, AI/ML learner
Self-study across maths, ML and Python
Graphs and intuition are missing from text explanations
Visual Pattern Lab with interactive parameters and similar questions
Secondary users: instructors reviewing class-level misconception patterns (Phase 3 analytics; not in MVP). Competition judges are an evaluation audience and need the benchmark view (section 17).
6. User Stories
Priority: M = must work in MVP, S = should, C = could, later phase.
ID
As a student I want to…
So that…
Priority
Testable criterion
US-01
Submit an answer with my reasoning
The system can find my misconception
M
Reasoning text field present; saved with the attempt
US-02
See a plain-language reason my answer is wrong
I fix the idea, not the symbol
M
Diagnosis card shows label, explanation and confidence
US-03
Be told whether my error was careless or conceptual
I know what to practise
M
Each wrong attempt carries error_type of careless, conceptual or unclear
US-04
Get hints that do not reveal the answer
I still do the thinking
M
Answer-leakage check passes on 100% of shown hints
US-05
Get a different kind of help when the first fails
I do not get the same explanation again
M
After two failed turns the strategy changes; logged
US-06
Receive a fresh question after learning a concept
I can prove I understand
M
Transfer item differs from the taught example in values and context or structure
US-07
See how my mastery score was computed
I trust it
M
Breakdown lists evidence items and weights
US-08
See the actual graph for a function or inequality question
I understand visually
M
Graph rendered from validated spec with axes, labels, grid
US-09
Click "Generate Similar Question" and pick difficulty
I get more practice on the same pattern
M
New question, new graph, verified answer, no duplicate
US-10
Click "Change Pattern"
I test a related concept
S
Returns question from a linked pattern in the concept graph
US-11
Change a parameter and watch the graph update
I build intuition
S
Slider updates plot within 200 ms client-side
US-12
See my daily goal, streak and weak concepts
I know what to do next
M
Home shows all four from stored data
US-13
Follow a roadmap with prerequisites
I study in a sensible order
M
Locked node shows missing prerequisite
US-14
See a report of my misconceptions and whether they are resolved
I track progress
M
Evaluator lists each misconception with status and evidence count
US-15
Review past sessions
I revise mistakes
S
Sessions list with summaries (Phase 2)
US-16
Practise a mock interview or viva
I prepare for placements
C
Phase 2
US-17
Upload notes and ask questions about them
The tutor uses my material
C
Phase 2
US-18
Listen to a topic summary
I revise on the move
C
Phase 3
US-19
Report an issue or rate a lesson
The team improves the product
S
Feedback form saves with session context
7. Functional Requirements
Priority: P0 must work in MVP, P1 basic UI acceptable in MVP, P2 later phase.
ID
Requirement
Priority
Verified by
FR-01
Student can sign up, log in, and keep a persistent profile
P0
Auth integration test
FR-02
Every practice or tutor question is stored with concept tags and a canonical answer
P0
Schema test
FR-03
The system classifies each wrong attempt as careless, conceptual or unclear and, if conceptual, maps it to a misconception from the catalog
P0
Benchmark on held-out set
FR-04
The tutor selects one of eight teaching strategies per turn and records the choice, rationale and outcome
P0
Intervention log test
FR-05
The tutor never states the final answer before the hint ladder is exhausted, unless the student asks to give up
P0
Leakage detector
FR-06
After teaching, TransferProof issues a new item that is not a copy of any taught example
P0
Similarity check below threshold
FR-07
Mastery is computed from at least three independent evidence items across at least two sessions or two contexts
P0
Unit test of scoring function
FR-08
Graph and diagram data is returned as a typed JSON spec and rendered by the frontend
P0
Schema and render tests
FR-09
All specs and generated answers pass deterministic validation before display
P0
Validator test suite
FR-10
"Generate Similar Question" and "Change Pattern" work with easy, medium and hard
P0
End-to-end test
FR-11
Home shows daily goal, streak, progress, weak concepts and next activities
P0
UI test
FR-12
Roadmap shows concepts, dependencies, prerequisites and completion
P0
UI test
FR-13
Evaluator shows concept scores, misconception report and TransferProof results
P0
UI test
FR-14
Sessions, Library, Mind Map, Feedback modules
P1 (basic) / P2 (full)
Phase 2 criteria
FR-15
Roleplay, Workshop, Scenarios
P2
Phase 2 criteria
FR-16
Flopod audio learning
P2
Phase 3 criteria
FR-17
Model benchmark can be rerun from a single command and produces a report
P0
CI script
FR-18
Every model call is logged with input hash, output, latency, validator results
P0
Log inspection
8. Detailed Feature Specifications (13 modules)
Each module lists purpose, users, features and actions, screens, inputs and outputs, dependencies and acceptance criteria. Phase tags: MVP, P2 (Phase 2), P3 (Phase 3).
8.1 Home — MVP
• Purpose / users: one-glance status and next step for every student.
• Features / actions: daily goal ring (default 3 concepts or 20 minutes, editable); streak counter (day counts when at least one scored attempt is logged); progress overview by subject; top five weak concepts; three recommended activities with a reason string such as "Resolve 'off-by-one in loops' (2 of 3 checks failed)"; click-through to Practice, Roadmap or Ask Neuro.
• Screens: Dashboard.
• Inputs → outputs: attempts, mastery, misconception records → cards and recommendations from a rule-based recommender (due transfer checks first, then unresolved misconceptions, then next roadmap node).
• Dependencies: Evaluator data, Roadmap graph.
• Acceptance: all cards render with real data for a seeded student; recommendation reason is shown; empty state appears for a new user.
8.2 Ask Neuro — MVP
• Purpose / users: primary conversational tutor for all students.
• Features / actions: free-text question; attach current practice question as context; structured replies (diagnosis card, hint ladder, example, visual, check question); follow-ups; "I'm stuck", "Show another way", "Give me a similar question", "Test me" buttons; session context kept across turns.
• Screens: Chat with right-hand insight panel (misconception, strategy used, mastery).
• Inputs → outputs: message plus learner state → JSON turn object (section 15) rendered as components; never raw model text for diagnosis or graphs.
• Dependencies: teaching model, validators, Misconception DNA, TransferProof.
• Acceptance: a scripted five-turn session shows strategy change after a failed hint; a function question returns a rendered graph; hints pass the leakage check.
8.3 Roadmap — MVP
• Purpose / users: ordered learning path per subject.
• Features / actions: concept graph with prerequisites; node states locked, available, in progress, mastered; start a node; prerequisite warning when a misconception points to an earlier concept; completion percentage.
• Screens: Subject roadmap (list and graph toggle), node detail drawer.
• Inputs → outputs: concept graph, mastery → path with next recommended node.
• Dependencies: concept catalog, mastery calculator.
• Acceptance: seeded graph of at least 25 concepts across four subjects; a node cannot be marked mastered without TransferProof evidence.
8.4 Practice — MVP
• Purpose / users: question practice with adaptive support.
• Features / actions: topic filter; MCQ, short answer, coding (Python, run against test cases in a sandbox) and graph-based questions; reasoning box; hint request; Generate Similar Question; Change Pattern; difficulty selector.
• Screens: Practice list, Question view with Visual Pattern Lab panel.
• Inputs → outputs: answers and reasoning → verdict, diagnosis, next intervention.
• Dependencies: question bank, validators, code runner (P1 for coding).
• Acceptance: at least 60 seeded questions across four subjects; each wrong attempt gets an error-type label; coding questions may be MCQ-only in MVP.
8.5 Sessions — P2 (basic list in MVP optional)
• Purpose / users: history and revision.
• Features / actions: list sessions; summary (concepts, misconceptions seen, strategies that worked); reopen a past question; filter mistakes.
• Inputs → outputs: stored turns → generated summary (model call, cached).
• Dependencies: logging schema.
• Acceptance: every finished session has a summary with at least misconceptions and result counts.
8.6 Roleplay — P2
• Purpose / users: mock interviews and vivas for final-year students.
• Features / actions: choose role (interviewer, viva examiner, student for teach-back); topic and difficulty; scored rubric at the end; misconceptions from the roleplay feed Misconception DNA.
• Dependencies: Ask Neuro engine, rubric prompts.
• Acceptance: a ten-turn interview ends with concept-wise feedback saved to Evaluator.
8.7 Workshop — P2
• Purpose / users: guided, hands-on lessons.
• Features / actions: step-by-step lesson with embedded exercises and Visual Pattern Lab widgets; checkpoints that call TransferProof; resume where left off.
• Inputs → outputs: lesson definition (JSON) → interactive steps and completion record.
• Dependencies: lesson authoring format, Visual Pattern Lab.
• Acceptance: two authored lessons (for example binary search, linear regression) run end to end.
8.8 Scenarios — P2
• Purpose / users: applied problem solving and decisions.
• Features / actions: case with branching decisions; programming challenges; scored rationale; misconception tagging of weak reasoning.
• Dependencies: scenario authoring format, model.
• Acceptance: three scenarios with at least two decision points each.
8.9 Library — P2
• Purpose / users: personal notes and resources.
• Features / actions: PDF upload (max 20 MB), topic tagging, bookmarks, saved explanations from Ask Neuro, search; "ask about this document" using retrieval.
• Inputs → outputs: files → extracted text chunks and metadata.
• Dependencies: file storage, text extraction, retrieval index.
• Acceptance: upload, tag, search and bookmark work; MVP may expose only "save explanation".
8.10 Flopod — P3
• Purpose / users: audio revision.
• Features / actions: topic summary to speech, playback controls, revision playlist.
• Dependencies: a text-to-speech provider (to be chosen), approved summaries.
• Acceptance: a five-minute summary plays for any mastered or in-progress concept.
8.11 Mind Map — P2
• Purpose / users: see concept relationships.
• Features / actions: expandable node graph (React Flow) from the concept graph; colour by mastery; click a node to open Roadmap detail; highlight misconception links.
• Dependencies: concept graph, mastery data.
• Acceptance: the seeded graph renders and expands without overlap bugs for 100 nodes.
8.12 Evaluator — MVP
• Purpose / users: assessment and evidence of progress.
• Features / actions: concept scores with breakdown; misconception report (status: active, improving, resolved, with evidence counts); TransferProof results; timed assessment mode (P1); export report as PDF (P2).
• Inputs → outputs: attempts, interventions, transfer items → scores and report.
• Dependencies: all learning data.
• Acceptance: the mastery explanation lists each evidence item, its weight and recency effect; no concept is shown as mastered on a single correct answer.
8.13 Feedback — P2 (simple form in MVP)
• Purpose / users: collect product feedback and bug reports.
• Features / actions: rating, free text, category, auto-attached screen and session ID; thumbs on each tutor reply feeds a quality dataset.
• Acceptance: a submitted item is stored and visible in an admin query.
9. Four Signature Features
The model proposes; deterministic code checks and records. Wherever a rule says "system", it is code, not a prompt.
9.1 Misconception DNA
Behaviour. For every wrong or hesitant attempt the system produces a diagnosis object: error_type, misconception_id, confidence, evidence (the phrase or step that revealed it), prerequisite_concepts, and a plain-language explanation.
Careless vs conceptual. The system combines model output with rule signals before labelling.
Signal
Points to careless
Points to conceptual
Student solved a near-identical item correctly in the last 7 days
Yes
No
Reasoning text states the correct rule but the final step has a slip (sign, typo, off by one in arithmetic)
Yes
No
Wrong answer equals the predicted output of a catalog misconception
No
Yes (strong)
Same wrong pattern in two or more attempts
No
Yes
Reasoning text states a false rule
No
Yes
Answer submitted in under 20% of median time
Weak yes
No
Rule: label conceptual only if the model confidence is at least 0.6 and at least one non-model signal agrees; otherwise label unclear and ask one probing question. Thresholds are initial assumptions to tune on validation data.
Learner misconception profile. One row per (student, misconception) with status, first_seen, last_seen, occurrences, interventions_tried, resolved_at.
Status
Enters when
Leaves when
active
Diagnosed conceptual with confidence at least 0.6
Two consecutive correct answers on discriminating items
improving
Above
Three correct discriminating items across two sessions including one transfer item → resolved; a repeat error → active
resolved
Condition above
The same misconception is diagnosed again → regressed
Prerequisite link. Each catalog misconception lists root_concepts. If the same misconception recurs after two interventions, Roadmap inserts a prerequisite check on the first root concept.
Display. Diagnosis card with: "What you may be thinking", "Why that breaks here" (with a counterexample), and "Related earlier concept".
9.2 Adaptive Teaching Engine
The engine runs a loop each turn. The model suggests a strategy and the intervention text; code enforces the guardrails.
flowchart TD
  A[Student attempt + reasoning] --> B[Diagnose: error type, misconception, learner state]
  B --> C{Policy: choose strategy}
  C --> D[Generate intervention]
  D --> E{Guardrails: leakage, correctness, level cap}
  E -- fail --> D
  E -- pass --> F[Show to student]
  F --> G[Observe next response]
  G --> H{Improved?}
  H -- yes, solved --> I[Fade support, schedule TransferProof]
  H -- partial --> C
  H -- no, same error --> J[Mark strategy failed, switch strategy]
  J --> C
  I --> K[Log outcome to strategy statistics]
  J --> K
Strategy
Use when
Example intervention
Switch away when
Progressive hint
Student is close; error is a missed step
Level 1 nudge, level 2 names the concept, level 3 shows the next step only
Level 3 given and still wrong
Step-by-step explanation
Student has no plan
Break the method into steps and ask the student to do step 1
Student completes steps but not the whole
Example-based
Concept is unfamiliar
Solved example on the same pattern with different values
Student copies the example surface features
Counterexample
Conceptual error from an over-general rule
A case where the student's rule gives a visibly wrong result
Student cannot interpret the counterexample
Contrastive examples
Two concepts are confused
Show A and B side by side, ask which applies
Still picks wrong concept twice
Real-world analogy
Abstract idea not landing
Map idea to an everyday system, then map back
Analogy is misapplied
Simpler prerequisite question
Root concept looks weak
A one-step question on the prerequisite
Prerequisite passed (return to original)
Guided problem solving
Multi-step problem, student stalls mid-way
Ask a sequence of small questions, one decision each
Student solves two steps unaided (fade)
Required behaviours.
1. The final answer is not shown until the hint ladder is exhausted or the student chooses "show solution"; a revealed solution counts as zero evidence.
2. If a strategy fails twice for the same misconception, the next turn uses a different strategy; the same strategy is not reselected for that misconception in that session.
3. After a correct unaided step, support drops one level on the next turn.
4. Each turn logs: learner-state snapshot, chosen strategy, rationale, intervention text, validator results, and next-turn outcome (success, partial, fail).
5. Strategy statistics per student and per misconception are kept so the policy can prefer what worked before; with fewer than three observations the model's own choice stands.
Learner-state representation (passed to the model as compact JSON):
concept_id, mastery (0–1 with evidence count), active_misconceptions[], hint_level_used, attempts_on_item, strategies_tried[] with outcomes, recent_accuracy (last 5), time_ratio, prerequisite_mastery{}, frustration_flag (three failures in a row or explicit "I give up").
9.3 TransferProof
Flow. After a concept is taught or a misconception improves, the system schedules transfer checks. A check is a new item that keeps the concept and changes at least one of: numeric values, context story, or problem structure.
Transfer level
What changes
Evidence weight
Near
Values only
0.5
Medium
Values and context
0.8
Far
Different structure that needs the same concept (for example a graph read instead of a formula)
1.0
Rules.
• The item must not match any taught example: normalized text similarity below 0.8 and different numeric parameters, checked in code.
• The item and its answer are produced by a template or solver and verified deterministically (section 10).
• The same item is never reused for the same student.
• Credit per item: 1.0 if solved unaided; 0.75 with one hint; 0.5 with two; 0 if the answer is revealed or wrong.
Mastery score. Each evidence item i has credit c_i (0–1), weight w_i (transfer level times a recency factor of 0.9 per 14 days of age), and the score is a smoothed weighted average:
M = \frac{\alpha_0 + \sum_i w_i c_i}{\alpha_0 + \beta_0 + \sum_i w_i}, \quad \alpha_0 = 1,\ \beta_0 = 1
Mastered requires all of the following: M at least 0.80; at least three unassisted or one-hint transfer items; at least one medium or far item; evidence from at least two sessions; and no active misconception on that concept. Otherwise the status stays "in progress" and the explanation says which condition is missing. All parameters are initial assumptions to calibrate on pilot data.
9.4 Visual Pattern Lab
Specified in full in section 10. In summary: the model outputs a visual_spec JSON object; a validator recomputes every point and answer; the frontend renders it; "Generate Similar Question" creates new items from a pattern template with solver-verified answers.
10. Visual Pattern Lab Specification
The model never draws. It emits a visual_spec JSON object; backend validators recompute and verify every number; the frontend renders only validated specs.
10.1 Supported visual types
type
Content
Renderer
Phase
function_plot
One or more y = f(x) curves, parametric curves, inequalities, points, intercepts, asymptotes
JSXGraph (interactive) — alternative: function-plot or Mafs; confirm in spike
MVP
coordinate_geometry
Points, lines, segments, circles, polygons, shaded regions
JSXGraph
MVP
data_chart
Bar, line, scatter, histogram, regression line
Recharts
MVP
tree
Binary tree, BST, heap, with highlighted nodes
React Flow or custom SVG
MVP (BST only)
graph_structure
Nodes and edges, directed or weighted, BFS/DFS/shortest-path highlights
React Flow
P1
linked_structure
Linked list, stack, queue
Custom SVG
P1
algorithm_trace
Array with ordered steps (compare, swap, pivot) for sorting and searching
Custom React + step player
P1
flowchart / concept_diagram
Boxes and arrows with labels
React Flow
P2
ml_view
Decision boundary on 2D points, loss curve, confusion matrix, gradient-descent path
Recharts + JSXGraph
P2
10.2 Visualization schema (v1)
Every spec has schema_version, type, title, viewport, axes, elements[], annotations[], controls[], explanation. Elements are a closed set of typed objects; unknown fields are rejected.
{
  "schema_version": "1.0",
  "type": "function_plot",
  "title": "Two parabolas with different vertices",
  "viewport": {"xmin": -6, "xmax": 6, "ymin": -4, "ymax": 12},
  "axes": {"x": {"label": "x", "grid": true}, "y": {"label": "y", "grid": true}},
  "parameters": [{"id": "a", "label": "a", "min": -3, "max": 3, "step": 0.5, "default": 1}],
  "elements": [
    {"id": "f1", "kind": "function", "expr": "a*x^2 - 2*x - 3", "domain": [-6, 6], "legend": "f(x)", "style": "primary"},
    {"id": "f2", "kind": "function", "expr": "x + 1", "domain": [-6, 6], "legend": "g(x)", "style": "secondary"},
    {"id": "p1", "kind": "point", "x": 3, "y": 0, "label": "root", "derived_from": "f1.root"},
    {"id": "r1", "kind": "region", "inequality": "y >= x + 1", "style": "shade"}
  ],
  "annotations": [{"target": "p1", "text": "f(3) = 0", "kind": "callout"}],
  "restrictions": {"x": "real", "excluded": []},
  "explanation": "The curve crosses the x-axis where f(x) = 0."
}
Safety constraints.
• Expressions use a whitelist grammar: numbers, variables x, y, declared parameters, operators + - * / ^, and functions sin cos tan asin acos atan exp ln log sqrt abs floor ceil min max. No identifiers outside the whitelist, no attribute access, no strings, no eval.
• Limits: at most 8 elements per function plot, 200 nodes per graph structure, 2,000 points per series, expression length 200 characters, spec size 64 KB.
• All text fields are escaped and rendered as text, never as HTML.
• Every derived_from claim (root, vertex, intercept, intersection, extremum, asymptote) is recomputed by the backend; if absent, the point is treated as a free point and the system does not describe it as a computed feature.
10.3 Deterministic validation pipeline
A spec is displayed only if every step passes. Failure triggers up to two regeneration attempts, then a template fallback, then a text-only answer with a notice.
1. Schema check with Pydantic against schema v1.
2. Expression parse with SymPy using the whitelist; reject unknown symbols.
3. Domain sampling: 200 sample points per function; no NaN or infinity except at declared exclusions; values inside viewport or viewport flagged as clipped.
4. Feature recomputation: roots, intercepts, vertex, intersections, extrema and asymptotes solved symbolically or numerically; claimed points must match within 1e-6 (symbolic) or 1e-3 (numeric).
5. Inequality check: sampled points inside and outside the region satisfy or violate the inequality as drawn.
6. Annotation check: each annotation target exists and its text numbers match recomputed values.
7. Answer check: the stored answer is recomputed by the pattern solver and compared with the answer shown; for MCQs, exactly one option is correct and distractors are unequal to the answer.
8. Readability check: at most 4 curves with distinct styles; labels do not overlap (basic bounding-box test).
10.4 Generate Similar Question
flowchart LR
  Q[Current question] --> P[Identify pattern_id from stored tag, else model classifies then code confirms]
  P --> D[Choose difficulty: easy, medium, hard]
  D --> S[Sample parameters within pattern constraints]
  S --> M[Model writes context text if needed]
  M --> V[Solver computes answer + visual_spec]
  V --> C{Validation pipeline}
  C -- fail --> S
  C -- pass --> U{Duplicate check}
  U -- duplicate --> S
  U -- unique --> R[Show question + graph]
Pattern library. Each pattern is code plus config: pattern_id, concept_id, parameter ranges per difficulty, constraints (for example integer roots), solver function, visual builder, answer format, and related_patterns[] for Change Pattern. MVP target: 12 patterns across four subjects (examples below).
Subject
Example patterns
Mathematics
Quadratic roots and vertex; line intersection; linear inequality region; transformation of y = f(x); slope and rate of change
DSA
BST insertion and traversal; binary search steps; bubble sort pass trace
AI/ML
Linear regression fit read from scatter; gradient descent step on a parabola; decision boundary classification
Python
Loop trace table (rendered as table, not graph)
Difficulty. Easy: integer values, one concept step, visual shows answer features. Medium: two steps or fractions, some features unlabelled. Hard: three steps, negative or non-integer values, context story, or an inverse question (from graph to equation). Difficulty is defined by parameter ranges and step count in pattern config, not by the model's opinion.
Duplicate prevention. Canonical hash of (pattern_id, normalized parameters) checked against all questions the student has seen; plus text similarity below 0.85 to the last 20 seen. If unique parameters run out, the system reports it and offers Change Pattern.
Change Pattern. Picks a related_pattern that shares the concept family but needs a different reasoning step (for example from "find roots" to "identify vertex from graph"). The reason is shown: "Same idea, different angle: reading the graph instead of solving."
Generate from the current graph. The student can ask for a question about the displayed visual; the system chooses a pattern whose builder accepts the current parameters.
10.5 Visual interaction requirements
Interaction
Requirement
Explore
Pan, zoom, reset; hover coordinates on curve
Parameter sliders
Declared in parameters[]; plot updates client-side in under 200 ms; derived points recomputed client-side from the same expression
Compare two graphs
Two specs overlaid, or side by side with linked axes; legend states the difference
Explain features
"Explain this graph" produces a text explanation from validated features only (roots, vertex, intercepts, monotonic intervals)
Ask about the visual
Chat input carries the spec ID and current parameter values as context
Accessibility
Text summary and data table alternative for every visual; colour plus line-style distinction
10.6 Acceptance criteria
• 100 generated specs per pattern pass the pipeline in an automated test with 0 invalid specs displayed.
• A deliberately corrupted spec (wrong vertex, unknown function, oversized) is rejected in tests.
• Generate Similar Question returns a unique, solver-verified question with graph in under 3 seconds at the 90th percentile (assumption).
• Duplicate test: 50 consecutive generations on one pattern and difficulty contain 0 repeats while the parameter space allows.
11. User Journey Maps
11.1 Core learning journey (MVP)
flowchart TD
  A[Sign in, pick subject and goal] --> B[Home: see weak concepts and next activity]
  B --> C[Practice question with graph]
  C --> D{Answer correct?}
  D -- no --> E[Misconception DNA diagnosis]
  E --> F[Adaptive hint or strategy]
  F --> G{Resolved this turn?}
  G -- no --> F2[Switch strategy] --> F
  G -- yes --> H[TransferProof: new unseen question]
  D -- yes --> H
  H --> I{Transfer passed?}
  I -- no --> E
  I -- yes --> J[Mastery evidence updated with explanation]
  J --> K[Evaluator + Roadmap update]
  K --> B
11.2 Journey table
Stage
Student does
System does
Emotion risk
Design response
Arrive
Opens Home
Shows next best activity with a reason
Overwhelm
Max three recommendations
Attempt
Answers and writes reasoning
Stores attempt, checks answer
Reasoning box feels like extra work
Optional but prompted; one-line placeholder
Stuck
Clicks "I'm stuck"
Diagnoses, selects strategy
Fear of being judged
Neutral wording: "Here's a common way this goes wrong"
Fail again
Repeats error
Marks strategy failed, switches
Frustration
Tone shift, offers simpler prerequisite question
Understand
Solves unaided
Fades support
Premature confidence
Announces "Now let's test it on something new"
Prove
Solves transfer item
Updates mastery with breakdown
Disappointment if not yet mastered
Show which condition is missing and how to meet it
Review
Opens Evaluator
Shows misconception status
—
Positive framing of resolved items
12. Screen-by-Screen Requirements
#
Screen
Key components
Primary actions
Data in
States to design
S1
Sign in / onboarding
Email-password form, subject picker, daily goal
Create account, choose subjects
User
Error, loading
S2
Home
Goal ring, streak, progress bars, weak concepts list, recommendation cards
Start recommended activity
Mastery, misconceptions
Empty (new user), loading skeleton, error
S3
Ask Neuro
Message list, composer, diagnosis card, hint ladder, visual panel, insight sidebar, quick-action chips
Send, "I'm stuck", "Test me", "Similar question"
Session turns
Streaming, model error with retry, validation-failed fallback, empty
S4
Practice list
Subject and topic filters, question cards with difficulty and status
Open question
Question bank
Empty filter result
S5
Question view
Question, optional graph, answer input, reasoning box, hint button, Generate Similar Question, difficulty selector, Change Pattern
Submit, hint, generate
Question, spec
Wrong, correct, hint level, generating, generation failed
S6
Roadmap
Subject tabs, concept graph/list, node states, prerequisite warnings, progress
Start node, view prerequisites
Concept graph
Locked, empty, loading
S7
Concept detail drawer
Mastery score, evidence list, misconceptions, start check
Start TransferProof
Mastery
No evidence yet
S8
Evaluator overview
Concept score table, trend chart, misconception report, TransferProof results
Open breakdown
Scores
No data, partial data
S9
Mastery breakdown modal
Evidence items with weights, formula summary, missing conditions
Close, start check
Evidence
—
S10
Benchmark report (judge view)
Table comparing three systems, metric definitions, sample transcripts
Rerun, export
Eval results
Not yet run
S11
Feedback modal
Rating, category, text
Submit
Session context
Sent, error
13. UI/UX Design Guidelines
Principles. (1) The learner's thinking comes first: reasoning input is always visible. (2) Insights are separate from conversation: diagnosis and mastery live in cards, not buried in chat prose. (3) Calm density: dark, spacious, few colours. (4) Everything shown is explainable: scores and diagnoses open to evidence. (5) Visuals are first-class: graphs get as much space as text.
Colour palette (dark-first).
Token
Hex
Use
bg-base
#0A0A0F
App background
bg-surface
#14141C
Cards, sidebar
bg-raised
#1C1C27
Hover, inputs
border-subtle
#2A2A3A
Dividers and card borders
accent-500
#8B5CF6
Primary buttons, active nav
accent-600
#7C3AED
Pressed state
accent-300
#C4B5FD
Links, highlights
text-primary
#F4F4F8
Body and headings
text-muted
#A1A1B5
Secondary text
success
#34D399
Correct, resolved
warning
#FBBF24
Careless error, unclear
danger
#F87171
Conceptual error, failure
info
#38BDF8
Hints and insights
Gradients: subtle violet-to-transparent on hero cards and the active nav item; borders use 1 px border-subtle with a violet glow on focus. All text pairs must reach WCAG 2.2 AA contrast (4.5:1 body, 3:1 large text); to be verified with a contrast checker before design freeze.
Typography. Inter for UI (14 px body, 16 px chat, 20/24/32 px headings), JetBrains Mono for code and equations. Line height 1.5 for chat text.
Spacing and layout. 4 px base unit with a scale of 4, 8, 12, 16, 24, 32, 48. Cards radius 12 px; max chat width 760 px; dashboard grid of 12 columns with 24 px gutters.
Sidebar. Persistent left sidebar, 264 px expanded and 72 px icon-only collapsed (toggle remembered). Order: Home, Ask Neuro, Roadmap, Practice, Sessions, Roleplay, Workshop, Scenarios, Library, Flopod, Mind Map, Evaluator, Feedback. Modules not yet built show a "Soon" badge and an empty state. On tablet the sidebar collapses by default; on mobile it becomes a bottom bar with five items (Home, Ask Neuro, Practice, Roadmap, More).
Content types are visually distinct.
Content
Treatment
Student message
Right-aligned, bg-raised, no accent
Neuro explanation
Left-aligned, bg-surface, 3 px violet left border
Diagnosis card
Full-width card with danger or warning header chip and "Why?" expander
Hint
info coloured chip with hint level (1–3)
Graph or diagram
Bordered card, own toolbar (reset, zoom, compare), caption and text alternative
Learning insight (mastery, streak)
Compact pill or card in the insight sidebar, never inside the message stream
Component library (build first). Button, IconButton, Input, Textarea, Select, Tabs, Card, Chip, ProgressRing, ProgressBar, Modal, Drawer, Toast, Skeleton, EmptyState, Tooltip, Table, MessageBubble, DiagnosisCard, HintLadder, MasteryMeter, VisualCard, ConceptNode.
States. Loading uses skeletons, not spinners, for lists and cards; model replies stream with a typing indicator. Errors are inline with a retry action and a plain-language message. Validation-failed visuals say "I couldn't verify this graph, here is a text explanation". Empty states always say what to do next.
Accessibility. Keyboard operable everywhere including graph toolbar; visible focus ring; ARIA labels and live regions for streamed replies; no information by colour alone; reduced-motion setting disables animations; every visual has a text summary and data-table view; supports 200% zoom.
14. System Architecture
A modular monolith: one React app, one FastAPI service with internal modules, one PostgreSQL database, and one model inference endpoint. No other services are needed for the MVP.
flowchart LR
  subgraph Client[React + Vite + Tailwind]
    UI[Pages: Home, Ask Neuro, Practice, Roadmap, Evaluator]
    VIZ[Visual renderers: JSXGraph, Recharts, React Flow]
  end
  subgraph API[FastAPI modular monolith]
    AUTH[auth]
    TUTOR[tutor orchestrator]
    MDNA[misconception service]
    POLICY[teaching policy + guardrails]
    TP[transferproof + mastery]
    VPL[visual lab: patterns, solvers, validators]
    CONTENT[questions, concepts, roadmap]
    EVAL[benchmark runner]
  end
  DB[(PostgreSQL)]
  LLM[Fine-tuned teaching model endpoint]
  RUN[Python code sandbox - P1]
  UI -->|REST JSON| AUTH
  UI --> TUTOR
  VIZ --> VPL
  TUTOR --> MDNA --> LLM
  TUTOR --> POLICY --> LLM
  TUTOR --> VPL
  TP --> VPL
  AUTH --> DB
  TUTOR --> DB
  TP --> DB
  CONTENT --> DB
  EVAL --> LLM
  TUTOR --> RUN
Backend modules (Python 3.11+, FastAPI, SQLAlchemy, Alembic, Pydantic v2, SymPy).
Module
Responsibility
auth
Registration, login, token issue and refresh
tutor
Orchestrates a turn: loads state, calls model, validates, saves
misconception
Catalog, diagnosis post-processing, profile updates
policy
Strategy guardrails, switching rules, hint ladder, strategy statistics
transfer
Schedules checks, creates items, computes mastery
visual
Pattern library, solvers, spec schema, validators, duplicate guard
content
Concepts, prerequisites, question bank, roadmap
eval
Benchmark harness and reports
llm_client
One interface over the model endpoint with timeouts, retries, logging
Frontend modules (React 18, Vite, Tailwind, TypeScript, TanStack Query, React Router). app-shell (sidebar, routes, theme), chat, practice, visual-lab (renderers per spec type behind one VisualCard), roadmap, evaluator, design-system. Charts: Recharts for data charts; JSXGraph for interactive mathematics; React Flow for graphs, trees and concept maps.
Model inference flow.
1. Frontend sends message or attempt with session_id.
2. Orchestrator loads learner state and recent turns (last 6) and builds the compact prompt.
3. llm_client calls the model with a JSON-schema constrained output (if the endpoint supports it) or a parse-and-repair step.
4. Pydantic validates the turn object; the visual validator, leakage detector and answer checker run.
5. On failure: one repair attempt, then regenerate once, then fall back to a static hint from the question bank and flag the turn.
6. Save turn, diagnosis, intervention and validator results; return to the client.
Authentication and sessions. Email and password with Argon2 hashing; short-lived access token (15 min) and refresh token in an HTTP-only secure cookie; a tutoring session is a database row (sessions) with a 30-minute idle timeout. OAuth is deferred.
File handling. MVP stores no uploads. Phase 2: PDFs up to 20 MB to object storage, type-checked and size-limited, text extracted server-side.
Error handling and logging. Uniform error body {code, message, request_id}; structured JSON logs with request ID; separate model_calls table (input hash, latency, token counts, validator verdicts). No raw student free text in application logs.
Deployment. Frontend on a static host or CDN; backend in one container with Uvicorn behind a reverse proxy; managed PostgreSQL; model endpoint hosted by the training platform or a GPU host (decision D2). Environments: local Docker Compose, one staging, one production. Secrets in environment variables.
15. AI Model Architecture
What the model must learn. Five skills, trained in one multi-task instruction format: (1) diagnose the misconception behind a wrong attempt, (2) choose a teaching strategy given learner state, (3) write the intervention (hint level, example, counterexample, analogy, prerequisite question) without leaking the answer, (4) emit valid visual_spec JSON for visual questions, (5) write similar-question context and distractors within a pattern's parameters.
Hybrid design. The model handles language and judgement. Code handles anything checkable: correct answers, graph numbers, duplicates, leakage, mastery. This keeps the research contribution (strategy selection and misconception diagnosis) measurable and the product safe.
Base model. A small instruction-tuned open model (about 7–8B parameters) is preferred for latency and cost; the exact model must come from the platform's supported list (D1). Public AutoScientist adapters exist on Llama-3.3-70B, Llama-4-Scout and Mixtral, so larger models are supported, but 70B-class inference is probably too slow for a live demo unless hosted.
Input (one JSON object per call).
{
  "task": "teach_turn",
  "subject": "mathematics",
  "concept_id": "quadratic.vertex",
  "question": {"id": "q_182", "text": "...", "pattern_id": "quad_vertex_v1", "visual_spec": null},
  "student_attempt": {"answer": "-2", "reasoning": "The vertex is where x = b/2a", "correct": false},
  "learner_state": {"mastery": 0.42, "active_misconceptions": ["sign_error_vertex"], "hint_level_used": 0,
    "strategies_tried": [{"name": "progressive_hint", "outcome": "fail"}], "recent_accuracy": 0.4},
  "history": ["...last 6 turns..."]
}
Output (strict JSON).
{
  "diagnosis": {"error_type": "conceptual", "misconception_id": "sign_error_vertex", "confidence": 0.78,
    "evidence": "x = b/2a", "root_concepts": ["quadratic.standard_form"], "explanation": "..."},
  "strategy": {"name": "counterexample", "rationale": "Hint failed; rule is over-general", "hint_level": null},
  "intervention": {"text": "...", "asks_student_to": "predict the vertex of x^2 - 4x"},
  "visual_spec": null,
  "next_check": {"type": "observe_reply"}
}
Misconception classification. Closed-set classification over the catalog plus none and other (the model may flag a new, unseen error; these are logged for catalog review rather than acted on at high confidence). Confidence comes from token log-probabilities of the label if available, otherwise from a calibration set (D4).
Strategy selection. Closed set of eight strategy names. Training labels come from a documented decision table (section 9.2) validated by two reviewers; the model learns the table plus judgement on ambiguous states. The policy layer overrides the model only for hard rules (switch after two failures, no answer reveal).
Example and counterexample generation. Seeded from the catalog entry (wrong rule, a case where it fails), so the model rephrases verified material instead of inventing it. Numeric claims in examples are re-evaluated by the solver where a pattern exists.
Adaptive intervention logic. Defined in code (section 9.2). The model supplies the proposed strategy and wording; strategy statistics bias the choice but never remove the guardrails.
Structured graph generation. The model may propose a visual_spec for free-form questions in Ask Neuro; for Practice and TransferProof the spec is built by pattern code and the model contributes only text. This limits the damage of a model graph error.
Model evaluation. See section 17.
16. Training Dataset Strategy
16.1 Platform facts and open questions
Public pages describe Adaption's AutoScientist as a system that co-optimizes training data and the training recipe, with Adaptive Data recipes such as deduplication and reasoning-trace generation, and published adapters built with it use LoRA fine-tuning. Pages also report that the launch trial was free for 30 days from mid-May 2026. We do not assume current credits, supported base models, custom-dataset format, preference optimization, or weight export; these are decisions D1–D3 to confirm in the platform's own documentation and account before the build starts.
16.2 Training pipeline
flowchart TD
  A[Misconception catalog: ~60 entries, 4 subjects] --> B[Problem templates with solvers]
  B --> C[Programmatic wrong answers from catalog rules]
  C --> D[Student-attempt simulator + reasoning text]
  D --> E[Teacher LLM writes interventions per strategy]
  E --> F[Automatic validation: schema, leakage, solver, label checks]
  F --> G[Human review of a sample]
  G --> H[Dedup + split by misconception, template, topic]
  H --> I[Upload to AutoScientist / Adaptive Data]
  I --> J[Stage 2: fine-tune]
  J --> K[Stage 3: benchmark vs base and static tutor]
  K --> L{Stage 4 available and time left?}
  L -- yes --> M[Preference pairs + preference optimization]
  L -- no --> N[Ship Stage 2 model]
  M --> K
16.3 Data construction
Source
What it provides
Why it is trustworthy
Misconception catalog (team-authored, about 15 per subject)
Wrong rule, predicted wrong answer, counterexample, root concepts, careless-error look-alikes
Written and reviewed by team; predicted answers checked by code
Problem templates with solvers (about 40 in MVP)
Questions, correct answers, graph specs
Answers computed, not generated
Attempt simulator
Wrong answers from the catalog rule, careless slips (sign flip, off by one), correct answers, reasoning text in varied student voices
Labels are known by construction
Teacher LLM (different model family from the fine-tuned base)
Intervention text per strategy, analogies, dialogue turns
Constrained by catalog entry and validated
Strategy-selection set
Learner-state to strategy rows
Labels from the decision table, then reviewed by two people on a sample
Preference pairs (Stage 4)
Chosen: non-leaking, correct strategy; rejected: leaking, wrong strategy or repeated failed strategy
Built by code from known violations
No real student data is used in the MVP. No copyrighted question banks or textbook passages are copied; templates are original.
Target size (assumption). 3,000–6,000 examples for supervised fine-tuning, balanced across four subjects, eight strategies and all catalog misconceptions, including 15% careless-error examples and 10% "no misconception" correct-but-unexplained examples. Adaptive Data augmentation may expand this, but the held-out test set is never augmented.
Task mix. Diagnosis 30%, strategy selection plus intervention 40%, visual spec 15%, similar-question text 10%, refusal-to-leak cases 5%.
16.4 Validation
1. Schema: every output parses against the turn schema.
2. Solver: any number in an example, counterexample or graph spec is recomputed.
3. Leakage: hint-level interventions are rejected if they contain the final answer or its trivial paraphrase (string and numeric match, plus a model judge for paraphrase).
4. Label consistency: the labelled misconception must produce the shown wrong answer by catalog rule; careless-labelled items must not.
5. Judge cross-check: a second model scores pedagogical quality 1–5 on a rubric; below 3 is dropped.
6. Human review: at least 300 examples (or 10%) reviewed by two team members; agreement and error rate reported; if the error rate exceeds 5%, regenerate that slice.
16.5 Deduplication
Exact-match on normalized text; near-duplicate removal with embedding cosine similarity above 0.92 within a split; template-level cap (no more than 15 examples per template and parameter-bucket); Adaptive Data deduplication recipe may be used for training data only after splitting.
16.6 Splits and leakage control
Split
How it is made
Share
Test (frozen)
All examples of 15% of misconceptions, all examples of 20% of templates, and one entire topic per subject, selected before any training
About 20–25%
Validation
Random from remaining data, grouped by template so no template spans train and validation
About 10%
Train
Everything else
About 65–70%
The test set is built and hashed first; a script asserts no template ID, misconception ID, or near-duplicate text appears across test and train. Teacher-LLM prompts for test items use different seeds and are not shown to the platform's data-improvement recipes.
Limits of synthetic data. Synthetic students follow catalog rules, so they are more consistent than real learners. Results on this data show that the model reproduces intended teaching behaviour on unseen misconceptions and templates. They do not prove that students learn more.
17. Benchmark and Evaluation Strategy
17.1 Systems compared
System
Description
B0 Base model
Same base model, careful prompt with the schema and strategy definitions, no fine-tuning
B1 Static hint tutor
Rule-based: fixed three-level hint list stored with each question, then solution; no diagnosis
NT NEUROTEACH model
Fine-tuned model inside the full pipeline
NT-ablation (optional)
Fine-tuned model without the policy layer, to show the model's own contribution
All systems see identical inputs, temperature 0, and the same validators. B1 produces no diagnosis, so diagnosis metrics apply to B0 and NT only.
17.2 Metrics
Targets are proposed hypotheses to be revised after the first baseline run, not promises.
Metric
Definition
Method
Proposed target
Misconception identification accuracy
Exact match of misconception_id on held-out test attempts (macro-F1 also reported)
Automatic vs known label
NT at least 15 points above B0
Careless vs conceptual accuracy
Correct error_type
Automatic
At least 85%
Strategy selection accuracy
Match with decision-table label; also acceptance by blind human raters when several strategies are valid
Automatic + human on 100 items
NT at least 15 points above B0
Hint usefulness
Mean 1–5 rating on a rubric (relevance, specificity, appropriately partial)
Blind LLM judge from another family + human check on 100
NT above B0 and B1
Answer leakage rate
Share of hint-level interventions containing the answer or trivial restatement
Automatic detector + judge
At most 2%
Example correctness
Share of examples and counterexamples whose numbers and claims pass the solver or rubric
Automatic where solver exists, human otherwise
At least 95%
Graph specification validity
Share of generated specs passing schema + semantic validation; reported both raw (before repair) and after pipeline
Automatic
Raw at least 90%; shown 100%
Similar-question correctness
Share of generated questions with correct answer, valid visual, non-duplicate
Automatic + human on 50
100% shown; raw reported
Independent problem-solving accuracy
Simulated student solves a fresh item unaided after the tutoring episode
Student simulator
Report; NT at least B1
Transfer performance
Simulated student accuracy on far-transfer items from unseen templates
Student simulator
Report; NT at least B1
Interventions required
Mean turns until the simulated misconception is resolved
Student simulator
NT fewer than B1 and B0
User satisfaction
5-point rating after a session; SUS questionnaire in the pilot
Pilot users
Report; no target
17.3 Procedure
1. Freeze test set and scoring scripts; record hashes and model versions.
2. Run B0, B1, NT on the identical test inputs (one command, make benchmark).
3. Score automatically; send random 100 items per system pair for blind human or cross-family judge review.
4. Run the student-simulator episodes: 200 episodes per system with fixed seeds, covering held-out misconceptions.
5. Report mean with 95% bootstrap confidence intervals; paired comparisons use McNemar's test for accuracies and the Wilcoxon signed-rank test for scores; report effect sizes.
6. Publish failure examples (at least ten per system) beside the numbers.
Report format. One table (metric by system with confidence intervals), one bar chart for headline metrics, a leakage and validity section, ten annotated transcripts, and a limitations paragraph that states the synthetic-data boundary.
17.4 Automated evaluation versus learner outcomes

Automated model evaluation
Learner-outcome experiment
Question
Does the model behave as designed on unseen cases?
Do students learn more?
Subjects
Test set and simulated students
Real students, consent obtained
Evidence level
Technical performance
Educational effect
In MVP
Yes (required)
Optional small pilot: 15–30 students, two arms (static hint tutor vs NEUROTEACH), pre-test, post-test, delayed transfer test after 7 days; exploratory only
No claim of improved learning is made unless the pilot is run, and even then results are described as preliminary.