import React, { useState } from 'react';
import {
  Target,
  ArrowRight,
  AlertTriangle,
  Sparkles,
  BrainCircuit,
  Compass,
  Award
} from 'lucide-react';
import { DEMO_MISCONCEPTIONS, DEMO_NOTICE } from '@/data/demoData';

interface HomePageProps {
  onNavigate: (page: string) => void;
}

interface MisconceptionSummary {
  id: string;
  name: string;
  subject: string;
  wrong_rule: string;
  status: string;
  evidence_count: number;
  occurrences: number;
  last_seen: string;
}

export const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  const [selectedSubjectFilter, setSelectedSubjectFilter] = useState<string>('all');
  const [completedActions, setCompletedActions] = useState<string[]>([]);

  const handleActionClick = (actionId: string, targetNav: string) => {
    setCompletedActions((prev) => [...prev, actionId]);
    onNavigate(targetNav);
  };

  const filteredMisconceptions = selectedSubjectFilter === 'all'
    ? DEMO_MISCONCEPTIONS
    : DEMO_MISCONCEPTIONS.filter(m => m.subject === selectedSubjectFilter);

  return (
    <div className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-6 overflow-y-auto bg-bg-base transition-colors">
      {/* Notice Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs px-4 py-2.5 rounded-xl bg-bg-surface border border-border-subtle shadow-xs gap-2">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-accent-cyan" />
          <span className="text-accent-cyan font-bold">NEUROTEACH AI Platform</span>
          <span className="text-text-secondary">• Socratic Pedagogical Companion</span>
        </div>
        <span className="text-text-muted text-[11px]">{DEMO_NOTICE}</span>
      </div>

      {/* Hero Welcome & Daily Goal Banner */}
      <div className="p-6 md:p-8 rounded-2xl bg-bg-surface border border-border-subtle shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-lavender dark:bg-[#241E3E] text-accent-700 dark:text-accent-300 text-xs font-semibold border border-accent-200 dark:border-accent-500/30">
            <Sparkles className="h-3.5 w-3.5 text-accent-500" />
            <span>Active Semester Sprint • Target: 90% Mastery</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-text-primary">
            Welcome back, <span className="text-accent-500">Sahil</span>
          </h2>
          <p className="text-sm text-text-secondary max-w-2xl leading-relaxed">
            Your personalized learning engine has prioritized <strong className="text-text-primary font-semibold">1 active misconception</strong> in Quadratic Functions and scheduled <strong className="text-text-primary font-semibold">2 transfer checks</strong> to cement long-term retention.
          </p>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => onNavigate('ask_neuro')}
              className="px-4 py-2.5 rounded-xl bg-accent-500 hover:bg-accent-600 text-white font-semibold text-xs transition-colors flex items-center gap-2 shadow-sm"
            >
              <BrainCircuit className="h-4 w-4" />
              <span>Resume Socratic Tutor</span>
            </button>
            <button
              onClick={() => onNavigate('practice')}
              className="px-4 py-2.5 rounded-xl bg-bg-surface hover:bg-bg-raised text-text-primary font-semibold text-xs transition-colors flex items-center gap-2 border border-border-subtle"
            >
              <Compass className="h-4 w-4 text-accent-cyan" />
              <span>Open Visual Lab</span>
            </button>
          </div>
        </div>

        {/* Goal Ring Card */}
        <div className="shrink-0 p-5 rounded-xl bg-bg-raised border border-border-subtle flex items-center gap-5">
          <div className="relative h-16 w-16 flex items-center justify-center">
            <svg className="h-16 w-16 transform -rotate-90">
              <circle
                cx="32"
                cy="32"
                r="26"
                stroke="currentColor"
                className="text-border-subtle"
                strokeWidth="5"
                fill="transparent"
              />
              <circle
                cx="32"
                cy="32"
                r="26"
                stroke="#7555D9"
                strokeWidth="5"
                strokeDasharray="163"
                strokeDashoffset="54"
                strokeLinecap="round"
                fill="transparent"
              />
            </svg>
            <span className="absolute text-xs font-mono font-bold text-text-primary">67%</span>
          </div>
          <div>
            <p className="text-xs text-text-muted">Daily Goal Progress</p>
            <p className="text-sm font-bold text-text-primary">2 of 3 Concepts</p>
            <p className="text-[11px] text-accent-cyan font-semibold mt-0.5">14m / 20m Studied Today</p>
          </div>
        </div>
      </div>

      {/* Main Grid: Priority Recommendations & Weak Concepts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recommended Activities */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <Target className="h-4 w-4 text-accent-500" />
              <span>Prioritized Socratic Interventions</span>
            </h3>
            <span className="text-xs font-semibold text-accent-500">Markov Failure-State Policy</span>
          </div>

          <div className="space-y-3">
            {/* Recommendation 1 */}
            <div className="p-5 rounded-xl bg-bg-surface border border-border-subtle hover:border-accent-200 dark:hover:border-accent-500/30 shadow-xs transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1.5 max-w-xl">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-rose-50 dark:bg-rose-950/60 text-danger border border-rose-200 dark:border-rose-900">
                    URGENT REVISION
                  </span>
                  <span className="text-xs text-text-muted">Mathematics • Quadratic Vertex</span>
                </div>
                <h4 className="text-sm font-bold text-text-primary">Sign Neglect in Axis of Symmetry x = -b / (2a)</h4>
                <p className="text-xs text-text-secondary leading-relaxed">
                  You substituted b=-4 as -4/(2a) instead of -(-4)/(2a), missing the negative sign. Let's inspect a counterexample.
                </p>
              </div>

              <button
                onClick={() => handleActionClick('rec_1', 'ask_neuro')}
                className="shrink-0 px-4 py-2 rounded-xl bg-accent-500 hover:bg-accent-600 text-white font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors shadow-xs"
              >
                <span>{completedActions.includes('rec_1') ? 'Revisit Turn' : 'Start Socratic Turn'}</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>

            {/* Recommendation 2 */}
            <div className="p-5 rounded-xl bg-bg-surface border border-border-subtle hover:border-accent-cyan/30 shadow-xs transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1.5 max-w-xl">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-50 dark:bg-amber-950/60 text-warning border border-amber-200 dark:border-amber-900">
                    DUE TRANSFER CHECK
                  </span>
                  <span className="text-xs text-text-muted">DSA • Binary Search</span>
                </div>
                <h4 className="text-sm font-bold text-text-primary">Off-by-One Loop Invariant Boundary</h4>
                <p className="text-xs text-text-secondary leading-relaxed">
                  Scheduled retention proof: Verify that setting low = mid on 2-element arrays causes an infinite loop.
                </p>
              </div>

              <button
                onClick={() => handleActionClick('rec_2', 'practice')}
                className="shrink-0 px-4 py-2 rounded-xl bg-accent-softcyan dark:bg-[#132B38] text-accent-cyan dark:text-[#38BDF8] border border-accent-cyan/30 font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors"
              >
                <span>Take Transfer Proof</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>

            {/* Recommendation 3 */}
            <div className="p-5 rounded-xl bg-bg-surface border border-border-subtle hover:border-accent-200 dark:hover:border-accent-500/30 shadow-xs transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1.5 max-w-xl">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-50 dark:bg-emerald-950/60 text-success border border-emerald-200 dark:border-emerald-900">
                    EXPLORATORY
                  </span>
                  <span className="text-xs text-text-muted">AI/ML • Optimization</span>
                </div>
                <h4 className="text-sm font-bold text-text-primary">Gradient Descent Step Sizing & Divergence</h4>
                <p className="text-xs text-text-secondary leading-relaxed">
                  Interactive visual experiment: Adjust the learning rate parameter to see oscillations around the minimum.
                </p>
              </div>

              <button
                onClick={() => handleActionClick('rec_3', 'practice')}
                className="shrink-0 px-4 py-2 rounded-xl bg-bg-raised hover:bg-accent-lavender dark:hover:bg-[#241E3E] text-accent-600 dark:text-accent-300 border border-border-subtle font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors"
              >
                <span>Launch Interactive Lab</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Weak Concepts & Misconception Ledger */}
        <div className="lg:col-span-4 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-warning" />
              <span>Misconception Ledger</span>
            </h3>
            <button
              onClick={() => onNavigate('evaluator')}
              className="text-xs text-accent-500 hover:underline font-semibold"
            >
              View All ➔
            </button>
          </div>

          {/* Subject Filter Pills */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {['all', 'mathematics', 'python', 'dsa'].map((sub) => (
              <button
                key={sub}
                onClick={() => setSelectedSubjectFilter(sub)}
                className={`px-3 py-1 rounded-full text-[11px] font-semibold uppercase tracking-wider transition-colors ${selectedSubjectFilter === sub
                    ? 'bg-accent-500 text-white shadow-xs'
                    : 'bg-bg-surface text-text-secondary hover:text-text-primary border border-border-subtle'
                  }`}
              >
                {sub}
              </button>
            ))}
          </div>

          <div className="space-y-3">
            {filteredMisconceptions.slice(0, 3).map((item: MisconceptionSummary) => (
              <div
                key={item.id}
                className="p-4 rounded-xl bg-bg-surface border border-border-subtle hover:border-accent-200 dark:hover:border-accent-500/30 transition-all shadow-xs"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-text-primary">{item.name}</span>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-bold capitalize border ${item.status === 'resolved'
                        ? 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-900 text-success'
                        : item.status === 'improving'
                          ? 'bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-900 text-warning'
                          : 'bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-900 text-danger'
                      }`}
                  >
                    {item.status}
                  </span>
                </div>

                <p className="text-[11px] text-text-secondary italic line-clamp-2 mb-2">
                  "{item.wrong_rule}"
                </p>

                <div className="flex items-center justify-between text-[10px] text-text-muted pt-2 border-t border-border-subtle">
                  <span>Subject: {item.subject}</span>
                  <span>{item.evidence_count} evidence points</span>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Mastery Snapshot Card */}
          <div className="p-4 rounded-xl bg-bg-surface border border-border-subtle space-y-3 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-text-primary flex items-center gap-1.5">
                <Award className="h-4 w-4 text-accent-500" />
                <span>Bayesian Mastery Index</span>
              </span>
              <span className="text-xs font-bold text-accent-500">0.76 M</span>
            </div>
            <div className="w-full bg-bg-raised h-2.5 rounded-full overflow-hidden">
              <div className="bg-accent-500 h-full rounded-full" style={{ width: '76%' }} />
            </div>
            <p className="text-[10px] text-text-secondary leading-relaxed">
              Calculated using Bayesian smoothed evidence weights: Near (0.5), Medium (0.8), Far (1.0).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
