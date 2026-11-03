import React, { useState } from 'react';
import { 
  ShieldCheck, 
  CheckCircle2, 
  Filter
} from 'lucide-react';
import { DEMO_MISCONCEPTIONS, DEMO_NOTICE } from '@/data/demoData';

interface MisconceptionItem {
  id: string;
  name: string;
  subject: string;
  wrong_rule: string;
  status: string;
  evidence_count: number;
  occurrences: number;
  last_seen: string;
}

export const EvaluatorPage: React.FC = () => {
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [activeTab, setActiveTab] = useState<'dna' | 'benchmark' | 'formula'>('dna');

  const filtered = selectedFilter === 'all'
    ? DEMO_MISCONCEPTIONS
    : DEMO_MISCONCEPTIONS.filter(m => m.subject === selectedFilter);

  return (
    <div className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-8 overflow-y-auto bg-bg-base">
      {/* Notice Banner */}
      <div className="p-4 rounded-card glass-panel border border-border-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2 text-accent-cyan">
          <ShieldCheck className="h-4 w-4 text-accent-cyan" />
          <span className="font-bold">Explainable Bayesian Smoothed Mastery & Misconception Ledger</span>
        </div>
        <span className="text-text-muted text-[11px] font-mono">{DEMO_NOTICE}</span>
      </div>

      {/* Mastery Score Formula Banner */}
      <div className="p-6 rounded-card glass-panel-elevated space-y-4 card-hover-3d relative overflow-hidden">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-white">Bayesian Smoothed Mastery Formula</h3>
            <p className="text-xs text-text-muted mt-0.5">Formal evidence integration across near, medium, and far transfer proofs.</p>
          </div>
          <span className="font-mono text-xs px-3 py-1.5 rounded-xl glass-pill text-accent-cyan border border-accent-cyan/30 font-bold shadow-sm">
            M = (α₀ + Σ wᵢ cᵢ) / (α₀ + β₀ + Σ wᵢ)
          </span>
        </div>

        <p className="text-xs text-text-muted leading-relaxed max-w-4xl">
          Where prior parameters α₀ = 1, β₀ = 1. Evidence items carry weights based on transfer depth: 
          <strong className="text-white"> Near Transfer = 0.5</strong>, <strong className="text-white">Medium Transfer = 0.8</strong>, <strong className="text-white">Far Transfer = 1.0</strong>, 
          discounted with a recency half-life. A concept cannot be declared Mastered on a single correct answer.
        </p>

        {/* View Switcher Tabs */}
        <div className="flex items-center gap-2 pt-2 border-t border-border-subtle">
          <button
            onClick={() => setActiveTab('dna')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'dna' ? 'bg-accent-500 text-white shadow-glow-violet' : 'glass-pill text-text-muted hover:text-white'
            }`}
          >
            Misconception DNA Ledger
          </button>
          <button
            onClick={() => setActiveTab('benchmark')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'benchmark' ? 'bg-accent-500 text-white shadow-glow-violet' : 'glass-pill text-text-muted hover:text-white'
            }`}
          >
            TransferProof Benchmark Table
          </button>
        </div>
      </div>

      {activeTab === 'dna' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Misconception DNA Report */}
          <div className="lg:col-span-12 space-y-4">
            <div className="p-4 rounded-card glass-panel flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white uppercase tracking-wider">Misconception DNA Tracker</span>
                <span className="text-text-muted">• {filtered.length} Recorded Mental Models</span>
              </div>

              {/* Subject Filter Buttons */}
              <div className="flex items-center gap-1.5 flex-wrap">
                <Filter className="h-3.5 w-3.5 text-text-muted mr-1" />
                {['all', 'mathematics', 'python', 'dsa'].map((sub) => (
                  <button
                    key={sub}
                    onClick={() => setSelectedFilter(sub)}
                    className={`px-2.5 py-1 rounded-lg text-[10px] font-mono uppercase tracking-wider transition-all ${
                      selectedFilter === sub
                        ? 'bg-accent-500 text-white font-bold shadow-sm'
                        : 'glass-pill text-text-muted hover:text-white'
                    }`}
                  >
                    {sub}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filtered.map((item: MisconceptionItem) => (
                <div 
                  key={item.id}
                  className="p-5 rounded-card glass-panel space-y-3 card-hover-3d border border-border-subtle"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-white">{item.name}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded font-mono uppercase bg-bg-raised text-accent-cyan border border-border-subtle">
                        {item.subject}
                      </span>
                    </div>

                    <span 
                      className={`text-[10px] px-2.5 py-0.5 rounded-full font-mono capitalize font-bold border ${
                        item.status === 'resolved'
                          ? 'bg-success/15 border-success/30 text-success'
                          : item.status === 'improving'
                          ? 'bg-warning/15 border-warning/30 text-warning'
                          : 'bg-danger/15 border-danger/30 text-danger'
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>

                  <div className="p-3.5 rounded-xl bg-bg-base/70 text-xs text-text-muted border border-border-subtle">
                    <span className="font-semibold text-accent-cyan block mb-1">Diagnosed Faulty Rule:</span>
                    <span className="italic leading-relaxed">{item.wrong_rule}</span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-text-muted pt-1 border-t border-border-subtle">
                    <span>Occurrences: <strong className="text-white">{item.occurrences}</strong></span>
                    <span>Evidence Points: <strong className="text-white">{item.evidence_count} checks</strong></span>
                    <span>Last Seen: <strong className="text-white">{item.last_seen}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'benchmark' && (
        <div className="p-6 rounded-card glass-panel-elevated space-y-6">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Held-Out Evaluation Benchmark (125 Items)</h3>
            <p className="text-xs text-text-muted mt-1">Comparison between baseline un-tuned model, static hint tutor, and fine-tuned NeuroTeach AI.</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-border-subtle text-text-muted font-mono uppercase">
                  <th className="py-3 px-4">Evaluation System</th>
                  <th className="py-3 px-4">Misconception Accuracy</th>
                  <th className="py-3 px-4">Answer Leakage Rate</th>
                  <th className="py-3 px-4">Visual Spec Validity</th>
                  <th className="py-3 px-4">Pedagogical Policy</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle">
                <tr className="hover:bg-bg-raised/40 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-text-muted">B0: Base Model (Un-tuned)</td>
                  <td className="py-3.5 px-4 font-mono text-warning">68.8%</td>
                  <td className="py-3.5 px-4 font-mono text-danger">12.0% (Leaks answer)</td>
                  <td className="py-3.5 px-4 font-mono text-text-muted">78.4%</td>
                  <td className="py-3.5 px-4 text-text-muted">Prompt-based</td>
                </tr>
                <tr className="hover:bg-bg-raised/40 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-text-muted">B1: Static Hint Tutor</td>
                  <td className="py-3.5 px-4 font-mono text-danger">0.0% (No diagnosis)</td>
                  <td className="py-3.5 px-4 font-mono text-success">3.2%</td>
                  <td className="py-3.5 px-4 font-mono text-success">100.0%</td>
                  <td className="py-3.5 px-4 text-text-muted">Static 3-level ladder</td>
                </tr>
                <tr className="bg-accent-500/10 font-bold text-white">
                  <td className="py-3.5 px-4 text-accent-cyan flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-accent-cyan" />
                    <span>NEUROTEACH AI (LoRA 819874ef)</span>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-success">86.4% (+17.6%)</td>
                  <td className="py-3.5 px-4 font-mono text-success">0.0% (Zero Leakage)</td>
                  <td className="py-3.5 px-4 font-mono text-success">100.0% (SymPy Verified)</td>
                  <td className="py-3.5 px-4 text-accent-300">8 Adaptive Strategies</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
