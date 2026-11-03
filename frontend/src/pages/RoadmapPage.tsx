import React, { useState } from 'react';
import { 
  CheckCircle2, 
  PlayCircle, 
  BookOpen, 
  Lock, 
  ChevronRight, 
  ShieldCheck
} from 'lucide-react';
import { DEMO_CONCEPTS } from '@/data/demoData';
import { ConceptNode, SubjectType } from '@/types';

interface RoadmapPageProps {
  onNavigate?: (page: string) => void;
}

export const RoadmapPage: React.FC<RoadmapPageProps> = ({ onNavigate }) => {
  const [selectedSubject, setSelectedSubject] = useState<SubjectType>('mathematics');
  const [activeConcept, setActiveConcept] = useState<ConceptNode | null>(DEMO_CONCEPTS[1]);

  const filteredConcepts = DEMO_CONCEPTS.filter((c: ConceptNode) => c.subject === selectedSubject);

  return (
    <div className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-6 overflow-y-auto bg-bg-base">
      {/* Subject Filter Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border-subtle">
        <div className="flex items-center gap-2 flex-wrap">
          {(['mathematics', 'python', 'dsa', 'ai_ml'] as SubjectType[]).map((subj) => (
            <button
              key={subj}
              onClick={() => {
                setSelectedSubject(subj);
                const firstMatching = DEMO_CONCEPTS.find(c => c.subject === subj);
                if (firstMatching) setActiveConcept(firstMatching);
              }}
              className={`px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all ${
                selectedSubject === subj
                  ? 'bg-accent-500 text-white shadow-glow-violet'
                  : 'glass-pill text-text-muted hover:text-white'
              }`}
            >
              {subj.replace('_', '/')}
            </button>
          ))}
        </div>

        <div className="text-[11px] text-text-muted font-mono flex items-center gap-2 glass-pill px-3 py-1 rounded-full">
          <ShieldCheck className="h-3.5 w-3.5 text-accent-cyan" />
          <span>Prerequisite Graph Enforced</span>
        </div>
      </div>

      {/* Main Roadmap Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Concept Graph List */}
        <div className="lg:col-span-8 space-y-4">
          <div className="p-4 rounded-card glass-panel flex items-center justify-between text-xs">
            <span className="font-bold text-white uppercase tracking-wider">Curriculum Learning Path</span>
            <span className="text-text-muted font-mono">{filteredConcepts.length} Concepts in this sequence</span>
          </div>

          <div className="space-y-3">
            {filteredConcepts.map((concept: ConceptNode, idx: number) => {
              const isSelected = activeConcept?.id === concept.id;
              return (
                <div
                  key={concept.id}
                  onClick={() => setActiveConcept(concept)}
                  className={`p-5 rounded-card border transition-all cursor-pointer flex items-center justify-between card-hover-3d ${
                    isSelected
                      ? 'glass-panel-elevated border-accent-500 shadow-glow-violet'
                      : 'glass-panel border-border-subtle hover:border-accent-500/30'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    {/* Status Icon */}
                    <div className="shrink-0">
                      {concept.status === 'mastered' && (
                        <div className="h-9 w-9 rounded-xl bg-success/15 border border-success/30 flex items-center justify-center text-success shadow-sm">
                          <CheckCircle2 className="h-5 w-5" />
                        </div>
                      )}
                      {concept.status === 'in_progress' && (
                        <div className="h-9 w-9 rounded-xl bg-accent-500/20 border border-accent-500/40 flex items-center justify-center text-accent-cyan shadow-glow-violet">
                          <PlayCircle className="h-5 w-5 animate-pulse" />
                        </div>
                      )}
                      {concept.status === 'available' && (
                        <div className="h-9 w-9 rounded-xl bg-info/15 border border-info/30 flex items-center justify-center text-info shadow-sm">
                          <BookOpen className="h-5 w-5" />
                        </div>
                      )}
                      {concept.status === 'locked' && (
                        <div className="h-9 w-9 rounded-xl bg-bg-base/70 border border-border-subtle flex items-center justify-center text-text-muted">
                          <Lock className="h-4 w-4" />
                        </div>
                      )}
                    </div>

                    {/* Concept Metadata */}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono text-accent-cyan font-bold">0{idx + 1}.</span>
                        <h4 className="text-sm font-bold text-white">{concept.title}</h4>
                      </div>
                      <p className="text-xs text-text-muted mt-1 max-w-lg leading-relaxed">{concept.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right hidden sm:block">
                      <span className="text-xs font-mono font-bold text-white">
                        {Math.round(concept.mastery_score * 100)}%
                      </span>
                      <span className="text-[10px] text-text-muted block font-mono">Mastery</span>
                    </div>
                    <ChevronRight className={`h-4 w-4 ${isSelected ? 'text-accent-cyan' : 'text-text-muted'}`} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Concept Detail Inspector */}
        <div className="lg:col-span-4 space-y-4">
          <div className="p-6 rounded-card glass-panel-elevated space-y-4 border border-border-subtle sticky top-20">
            {activeConcept ? (
              <>
                <div className="space-y-1">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-accent-cyan block">Selected Concept</span>
                  <h3 className="text-base font-bold text-white">{activeConcept.title}</h3>
                  <p className="text-xs text-text-muted leading-relaxed">{activeConcept.description}</p>
                </div>

                <div className="space-y-2 pt-2 border-t border-border-subtle">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-text-muted font-mono">Status:</span>
                    <span className="font-bold font-mono uppercase text-accent-cyan">{activeConcept.status.replace('_', ' ')}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-text-muted font-mono">Bayesian Evidence:</span>
                    <span className="font-bold text-white font-mono">{activeConcept.evidence_count} Transfer Checks</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-text-muted font-mono">Prerequisites:</span>
                    <span className="font-bold text-white font-mono">
                      {activeConcept.prerequisites.length > 0 ? activeConcept.prerequisites.join(', ') : 'Foundational Root'}
                    </span>
                  </div>
                </div>

                <div className="pt-2">
                  <div className="w-full bg-bg-base/80 h-2 rounded-full overflow-hidden border border-border-subtle">
                    <div
                      className="bg-gradient-to-r from-accent-500 to-accent-cyan h-full rounded-full transition-all"
                      style={{ width: `${Math.round(activeConcept.mastery_score * 100)}%` }}
                    />
                  </div>
                </div>

                <button
                  onClick={() => onNavigate ? onNavigate('practice') : null}
                  className="w-full py-2.5 rounded-xl bg-accent-500 hover:bg-accent-600 text-white font-semibold text-xs transition-all shadow-glow-violet flex items-center justify-center gap-2"
                >
                  <PlayCircle className="h-4 w-4" />
                  <span>Start Practice Session</span>
                </button>
              </>
            ) : (
              <p className="text-xs text-text-muted">Select a concept on the left to inspect its dependency structure.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
