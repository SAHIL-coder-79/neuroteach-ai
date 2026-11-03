import React, { useState } from 'react';
import { Sidebar, NavItemKey } from './components/layout/Sidebar';
import { TopNavbar } from './components/layout/TopNavbar';
import { HomePage } from './pages/HomePage';
import { AskNeuroPage } from './pages/AskNeuroPage';
import { PracticePage } from './pages/PracticePage';
import { RoadmapPage } from './pages/RoadmapPage';
import { EvaluatorPage } from './pages/EvaluatorPage';
import { EmptyState } from './components/common/StateCards';

export const App: React.FC = () => {
  const [currentNav, setCurrentNav] = useState<NavItemKey>('ask_neuro');
  const [collapsed, setCollapsed] = useState<boolean>(false);

  // Render active page based on sidebar selection
  const renderPage = () => {
    switch (currentNav) {
      case 'home':
        return <HomePage onNavigate={(page) => setCurrentNav(page as NavItemKey)} />;
      case 'ask_neuro':
        return <AskNeuroPage />;
      case 'practice':
        return <PracticePage />;
      case 'roadmap':
        return <RoadmapPage onNavigate={(page) => setCurrentNav(page as NavItemKey)} />;
      case 'evaluator':
        return <EvaluatorPage />;
      case 'sessions':
        return (
          <div className="flex-1 p-6 md:p-8 max-w-5xl mx-auto space-y-6 overflow-y-auto">
            <div className="p-6 rounded-xl bg-bg-surface border border-border-subtle">
              <h2 className="text-lg font-bold text-text-primary mb-2">Learning Sessions History</h2>
              <p className="text-xs text-text-secondary mb-6">Recent diagnostic dialogues, practice turns, and transfer proof attempts.</p>
              <div className="space-y-3">
                {[
                  { title: "Quadratic Vertex & Axis of Symmetry", time: "Today, 12:15 PM", score: "88% Accuracy", mis: "1 Misconception Diagnosed (Resolved)" },
                  { title: "Binary Search Boundaries & Invariants", time: "Yesterday, 4:30 PM", score: "75% Accuracy", mis: "Off-by-one Upper Bound" },
                  { title: "Gradient Descent Step Sizing", time: "2 days ago, 11:00 AM", score: "92% Accuracy", mis: "None (Direct Mastered)" },
                ].map((s, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-bg-raised border border-border-subtle flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-semibold text-text-primary">{s.title}</h4>
                      <p className="text-[11px] text-text-muted mt-0.5">{s.time} • {s.mis}</p>
                    </div>
                    <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-accent-lavender text-accent-700 dark:bg-[#241E3E] dark:text-accent-300 font-semibold border border-accent-200 dark:border-accent-800">
                      {s.score}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      case 'roleplay':
        return (
          <div className="flex-1 p-6 md:p-8 max-w-5xl mx-auto space-y-6 overflow-y-auto">
            <div className="p-6 rounded-xl bg-bg-surface border border-border-subtle">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-bold text-text-primary">Teach-Back Viva & Interview Roleplay</h2>
                  <p className="text-xs text-text-secondary">Simulated oral examination. Explain concepts in your own words to prove deep mastery.</p>
                </div>
                <span className="text-xs font-mono px-3 py-1 rounded-full bg-accent-softcyan dark:bg-[#132B38] text-accent-cyan dark:text-[#38BDF8] border border-accent-cyan/30 font-semibold">
                  Preview Active
                </span>
              </div>
              <div className="p-5 rounded-xl bg-bg-raised border border-border-subtle space-y-3">
                <span className="text-xs font-bold text-accent-500 uppercase tracking-wider block">Viva Scenario</span>
                <p className="text-sm font-semibold text-text-primary">"Explain why binary search requires sorted input and prove the worst-case time complexity is O(log n)."</p>
                <div className="pt-2">
                  <button 
                    onClick={() => setCurrentNav('ask_neuro')}
                    className="px-4 py-2 rounded-xl bg-accent-500 hover:bg-accent-600 text-white font-semibold text-xs transition-colors"
                  >
                    Start Viva Examination
                  </button>
                </div>
              </div>
            </div>
          </div>
        );
      case 'mind_map':
        return (
          <div className="flex-1 p-6 md:p-8 max-w-5xl mx-auto space-y-6 overflow-y-auto">
            <div className="p-6 rounded-xl bg-bg-surface border border-border-subtle">
              <h2 className="text-lg font-bold text-text-primary mb-2">Subject Knowledge Dependency Map</h2>
              <p className="text-xs text-text-secondary mb-6">Interactive directed acyclic graph (DAG) showing prerequisite concept relationships.</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { name: "Algebra & Linear Equations", status: "Mastered (1.0)", color: "text-success border-success/30 bg-emerald-50 dark:bg-emerald-950/40" },
                  { name: "Quadratic Vertex Form", status: "In Progress (0.76)", color: "text-accent-500 border-accent-300 dark:border-accent-700 bg-accent-lavender dark:bg-[#241E3E]" },
                  { name: "Calculus & Derivatives", status: "Prerequisite Locked", color: "text-text-muted border-border-subtle bg-bg-raised" },
                ].map((node, i) => (
                  <div key={i} className={`p-4 rounded-xl border ${node.color} space-y-2`}>
                    <h4 className="text-sm font-bold text-text-primary">{node.name}</h4>
                    <span className="text-[11px] font-mono block">{node.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      default:
        return (
          <div className="flex-1 p-12 max-w-4xl mx-auto flex items-center justify-center">
            <EmptyState
              title={`${currentNav.replace('_', ' ').toUpperCase()} Module`}
              description="Core pedagogical evaluation is focused on the Ask Neuro, Practice, Roadmap, and Evaluator modules."
              actionLabel="Return to Socratic Tutor"
              onAction={() => setCurrentNav('ask_neuro')}
            />
          </div>
        );
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-bg-base font-sans text-text-primary selection:bg-accent-500/20 selection:text-accent-700">
      {/* Persistent Left Sidebar */}
      <Sidebar
        currentNav={currentNav}
        onSelectNav={(key) => setCurrentNav(key)}
        collapsed={collapsed}
        onToggleCollapse={() => setCollapsed(!collapsed)}
      />

      {/* Main View Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Sticky Top Navbar */}
        <TopNavbar
          currentNav={currentNav}
          streakDays={4}
          dailyGoalProgress={{ current: 2, total: 3 }}
        />

        {/* Active Page Body */}
        <main className="flex-1 flex flex-col overflow-hidden relative">
          {renderPage()}
        </main>
      </div>
    </div>
  );
};

export default App;
