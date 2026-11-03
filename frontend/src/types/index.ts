export type SubjectType = 'python' | 'dsa' | 'ai_ml' | 'mathematics';

export type ErrorType = 'careless' | 'conceptual' | 'unclear';

export type MisconceptionStatus = 'active' | 'improving' | 'resolved' | 'regressed';

export type TeachingStrategy = 
  | 'progressive_hint'
  | 'step_by_step'
  | 'example_based'
  | 'counterexample'
  | 'contrastive'
  | 'analogy'
  | 'simpler_prerequisite'
  | 'guided_problem_solving';

export interface VisualSpec {
  schema_version: string;
  type: 'function_plot' | 'coordinate_geometry' | 'data_chart' | 'tree' | 'algorithm_trace';
  title: string;
  viewport?: { xmin: number; xmax: number; ymin: number; ymax: number };
  axes?: {
    x?: { label: string; grid: boolean };
    y?: { label: string; grid: boolean };
  };
  parameters?: Array<{
    id: string;
    label: string;
    min: number;
    max: number;
    step: number;
    default: number;
  }>;
  elements: Array<{
    id: string;
    kind: 'function' | 'point' | 'line' | 'region' | 'node';
    expr?: string;
    x?: number;
    y?: number;
    label?: string;
    style?: string;
    legend?: string;
    derived_from?: string;
  }>;
  annotations?: Array<{
    target: string;
    text: string;
    kind: string;
  }>;
  explanation?: string;
}

export interface QuestionItem {
  id: string;
  subject: SubjectType;
  concept_id: string;
  pattern_id: string;
  difficulty: 'easy' | 'medium' | 'hard';
  title: string;
  question_text: string;
  canonical_answer: string;
  visual_spec?: VisualSpec;
  hint_ladder: string[];
}

export interface MisconceptionDiagnosis {
  error_type: ErrorType;
  misconception_id: string;
  confidence: number;
  evidence: string;
  explanation: string;
  root_concepts: string[];
  counterexample?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'student' | 'neuro';
  text: string;
  reasoning?: string;
  diagnosis?: MisconceptionDiagnosis;
  strategy?: TeachingStrategy;
  hint_level?: number;
  visual_spec?: VisualSpec;
  timestamp: string;
}

export interface ConceptNode {
  id: string;
  subject: SubjectType;
  title: string;
  description: string;
  status: 'locked' | 'available' | 'in_progress' | 'mastered';
  mastery_score: number; // 0.0 - 1.0
  prerequisites: string[];
  evidence_count: number;
}
