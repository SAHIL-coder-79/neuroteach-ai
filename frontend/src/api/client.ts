/**
 * Central API Client for NEUROTEACH AI
 * Connects frontend to the FastAPI backend modular monolith.
 */

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface TurnApiRequest {
  subject: string;
  concept_id: string;
  question_text: string;
  canonical_answer: string;
  student_message: string;
  student_reasoning?: string;
  learner_state?: Record<string, any>;
}

export interface TurnApiResponse {
  diagnosis: {
    error_type: string;
    misconception_id: string;
    confidence: number;
    evidence: string;
    root_concepts?: string[];
    explanation: string;
    counterexample?: string;
  };
  strategy: {
    name: string;
    rationale: string;
    hint_level?: number | null;
  };
  intervention: {
    text: string;
    asks_student_to?: string;
  };
  visual_spec?: any;
  next_check?: {
    type: string;
  };
}

export interface HealthApiResponse {
  status: string;
  version: string;
  timestamp: string;
  database: string;
  db_connection: string;
  environment: string;
  model_provenance: {
    model_name: string;
    base_model: string;
    adapter_experiment_id: string;
    adapter_path: string;
    adapter_verified: boolean;
    inference_provider: string;
    is_ready: boolean;
    readiness_status: string;
    mock_fallback_enabled: boolean;
  };
}

export const api = {
  /**
   * Health & Provenance Probe
   */
  async getHealth(): Promise<HealthApiResponse> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed: HTTP ${res.status}`);
    return res.json();
  },

  /**
   * Process a pedagogical student turn
   */
  async processTurn(req: TurnApiRequest): Promise<TurnApiResponse> {
    const res = await fetch(`${API_BASE}/pedagogy/turn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail?.message || `Pedagogy turn failed: HTTP ${res.status}`);
    }
    return res.json();
  },

  /**
   * Generate a solver-verified similar question
   */
  async getSimilarQuestion(patternId = 'parabola_vertex', difficulty = 'medium') {
    const res = await fetch(`${API_BASE}/pedagogy/visual/similar-question?pattern_id=${patternId}&difficulty=${difficulty}`);
    if (!res.ok) throw new Error(`Failed to generate similar question: HTTP ${res.status}`);
    return res.json();
  },

  /**
   * Fetch full misconception catalog
   */
  async getMisconceptions() {
    const res = await fetch(`${API_BASE}/pedagogy/evaluator/misconceptions`);
    if (!res.ok) throw new Error(`Failed to fetch misconceptions: HTTP ${res.status}`);
    return res.json();
  },
};

