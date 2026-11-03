# NEUROTEACH AI — BUTTON & INTERACTION CHECKLIST

**Audit Date**: 2026-11-03  
**Standard**: Strict "No Dead Buttons" Enforcement  

| Page / Component | Interactive Element | Tested Action | Verified Status |
| :--- | :--- | :--- | :--- |
| **Sidebar** | Collapse/Expand Toggle | Toggles sidebar width between 64px and 20px smoothly with animated Chevron | **WORKING** |
| **Sidebar** | `Home` Nav Link | Switches active view to Home Dashboard | **WORKING** |
| **Sidebar** | `Ask Neuro` Nav Link | Switches active view to Conversational Socratic Tutor | **WORKING** |
| **Sidebar** | `Roadmap` Nav Link | Switches active view to Subject Prerequisite Curriculum Graph | **WORKING** |
| **Sidebar** | `Practice` Nav Link | Switches active view to Practice Arena with Visual Pattern Lab | **WORKING** |
| **Sidebar** | `Sessions` Nav Link | Switches active view to Longitudinal Session History | **WORKING** |
| **Sidebar** | `Roleplay` Nav Link | Switches active view to Socratic Peer Teaching Mode | **WORKING** |
| **Sidebar** | `Mind Map` Nav Link | Switches active view to Topological Knowledge Lattice | **WORKING** |
| **Sidebar** | `Evaluator` Nav Link | Switches active view to Bayesian Evaluator & Benchmark Table | **WORKING** |
| **Top Navbar** | Notification Bell Button | Opens and closes system notifications popover drawer | **WORKING** |
| **Top Navbar** | Close Notifications (X) | Dismisses notifications drawer | **WORKING** |
| **Home Page** | "Resume Socratic Tutor" Button | Routes to `AskNeuroPage` | **WORKING** |
| **Home Page** | "Open Visual Lab" Button | Routes to `PracticePage` with interactive canvas | **WORKING** |
| **Home Page** | Subject Filter Pills (`All`, `Math`, `Python`, `DSA`) | Dynamically filters Misconception Ledger cards | **WORKING** |
| **Home Page** | Recommendation Action Buttons | Routes directly to corresponding problem in `AskNeuroPage` or `PracticePage` | **WORKING** |
| **Home Page** | "View All ➔" Ledger Button | Routes to `EvaluatorPage` | **WORKING** |
| **Ask Neuro** | "New Chat" Button | Resets chat dialogue history to fresh welcome turn | **WORKING** |
| **Ask Neuro** | Subject Selector Tabs (`Math`, `Python`, `DSA`, `AI/ML`) | Changes active domain context | **WORKING** |
| **Ask Neuro** | Message Input Textarea | Accepts multiline reasoning (`Shift+Enter` = newline, `Enter` = send) | **WORKING** |
| **Ask Neuro** | "Send Turn" Button | Dispatches pedagogical turn to backend `POST /api/v1/pedagogy/turn` | **WORKING** |
| **Ask Neuro** | "I'm Stuck" Button | Triggers adaptive policy Markov down-step to `simpler_prerequisite` | **WORKING** |
| **Practice Page** | Problem Preset Buttons | Switches active problem statement, formula, and visual spec | **WORKING** |
| **Practice Page** | "Submit" Answer Button | Validates student answer against canonical invariant and shows verdict badge | **WORKING** |
| **Practice Page** | "Reveal Next Hint" Button | Steps through progressive hint ladder levels 1, 2, and 3 | **WORKING** |
| **Practice Page** | "Generate Similar Question" Button | Queries live backend `GET /api/v1/pedagogy/visual/similar-question` | **WORKING** |
| **Practice Page** | Curvature Slider ($a$) in GraphPanel | Real-time SVG canvas path re-calculation and vertex coordinate update | **WORKING** |
| **Evaluator Page** | `DNA Ledger` vs `Benchmark Table` Tabs | Toggles view between longitudinal tracking and 125-item benchmark | **WORKING** |
| **Evaluator Page** | Subject Filter Pills (`All`, `Math`, `Python`, `DSA`) | Filters misconception cards by subject | **WORKING** |
| **Roadmap Page** | Subject Filter Tabs (`Math`, `Python`, `DSA`, `AI/ML`) | Switches curriculum graph domain | **WORKING** |
| **Roadmap Page** | Concept Node Cards | Selects concept, updates progress bar, and displays prerequisites | **WORKING** |
| **Roadmap Page** | "Start Practice Session" Button | Routes directly to Practice Arena with selected concept parameters | **WORKING** |

