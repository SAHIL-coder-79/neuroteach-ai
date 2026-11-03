import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Flame, 
  Bell, 
  CheckCircle2, 
  X, 
  Volume2, 
  VolumeX, 
  Sun, 
  Moon 
} from 'lucide-react';
import { NavItemKey } from './Sidebar';
import { voiceAssistant } from '../../utils/voiceAssistant';

interface TopNavbarProps {
  currentNav: NavItemKey;
  streakDays: number;
  dailyGoalProgress: { current: number; total: number };
}

const TITLE_MAP: Record<NavItemKey, { title: string; subtitle: string }> = {
  home: { title: 'Home Dashboard', subtitle: 'At-a-glance learning metrics, daily goals and prioritized recommendations' },
  ask_neuro: { title: 'Ask Neuro', subtitle: 'Conversational tutor with Misconception DNA & 8 Adaptive Strategies' },
  roadmap: { title: 'Subject Roadmap', subtitle: 'Prerequisite-ordered learning graph with mastery verification' },
  practice: { title: 'Practice Arena', subtitle: 'Adaptive question solving with embedded Visual Pattern Lab' },
  sessions: { title: 'Past Sessions', subtitle: 'Longitudinal dialogue history and misconception revisions' },
  roleplay: { title: 'Roleplay & Viva', subtitle: 'Simulated technical interview and teach-back viva mode' },
  workshop: { title: 'Interactive Workshop', subtitle: 'Step-by-step hands-on guided lessons and visual checkpoints' },
  scenarios: { title: 'Applied Scenarios', subtitle: 'Branching real-world engineering problem cases' },
  library: { title: 'Study Library', subtitle: 'Saved explanations, notes and semantic resource retrieval' },
  mind_map: { title: 'Concept Mind Map', subtitle: 'Visual dependency graph powered by React Flow' },
  evaluator: { title: 'Evaluator & Mastery', subtitle: 'Evidence-based Bayesian mastery breakdown and benchmark report' },
  feedback: { title: 'Feedback & Diagnostics', subtitle: 'Session ratings and model diagnostic traces' },
};

export const TopNavbar: React.FC<TopNavbarProps> = ({
  currentNav,
  streakDays,
  dailyGoalProgress,
}) => {
  const currentInfo = TITLE_MAP[currentNav] || { title: 'NEUROTEACH', subtitle: 'Pedagogical AI Engine' };
  const [showNotifications, setShowNotifications] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return document.documentElement.classList.contains('dark') || 
             localStorage.getItem('neuroteach_theme') === 'dark';
    }
    return false;
  });

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('neuroteach_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('neuroteach_theme', 'light');
    }
  }, [isDark]);

  useEffect(() => {
    return voiceAssistant.subscribe((speaking) => {
      setIsSpeaking(speaking);
    });
  }, []);

  const handleVoiceToggle = () => {
    if (isSpeaking) {
      voiceAssistant.stop();
    } else {
      voiceAssistant.speakScreen();
    }
  };

  const handleThemeToggle = () => {
    setIsDark((prev) => !prev);
  };

  return (
    <header className="h-16 px-6 flex items-center justify-between bg-bg-surface border-b border-border-subtle sticky top-0 z-20 transition-colors">
      {/* Title & context */}
      <div className="flex flex-col">
        <h1 className="text-base font-bold text-text-primary tracking-tight flex items-center gap-2">
          <span>{currentInfo.title}</span>
          <span className="h-2 w-2 rounded-full bg-accent-cyan" />
        </h1>
        <p className="text-xs text-text-secondary hidden md:block">
          {currentInfo.subtitle}
        </p>
      </div>

      {/* Right-hand stats & controls */}
      <div className="flex items-center gap-3 relative">
        {/* Anti-Leakage Guard Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-accent-softcyan dark:bg-[#132B38] text-accent-cyan dark:text-[#38BDF8] border border-accent-cyan/30 text-xs font-semibold">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>Guardrails Active</span>
        </div>

        {/* Daily Streak Indicator */}
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FFF6E7] dark:bg-[#2C2114] text-warning dark:text-[#FBBF24] border border-warning/30 text-xs font-semibold">
          <Flame className="h-3.5 w-3.5 fill-warning text-warning" />
          <span>{streakDays} Day Streak</span>
        </div>

        {/* Goal Indicator */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-bg-raised text-xs text-text-secondary font-medium">
          <span>Daily Goal:</span>
          <span className="text-text-primary font-bold">{dailyGoalProgress.current}/{dailyGoalProgress.total} Concepts</span>
        </div>

        {/* Light / Dark Theme Toggle Button */}
        <button
          onClick={handleThemeToggle}
          title={isDark ? "Switch to Light Theme" : "Switch to Dark Theme"}
          className="h-8 w-8 rounded-full bg-bg-raised hover:bg-border-subtle flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors border border-border-subtle"
          aria-label="Toggle dark/light theme"
        >
          {isDark ? <Sun className="h-4 w-4 text-warning" /> : <Moon className="h-4 w-4 text-[#7555D9]" />}
        </button>

        {/* Voice Assistant Button */}
        <button
          onClick={handleVoiceToggle}
          title={isSpeaking ? "Stop Voice Assistant" : "Read Screen Aloud (Voice Assistant)"}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition-all ${
            isSpeaking
              ? 'bg-rose-50 dark:bg-rose-950/60 text-danger border border-danger/30'
              : 'bg-accent-lavender dark:bg-[#241E3E] text-accent-600 dark:text-accent-300 border border-accent-200 dark:border-accent-500/30 hover:opacity-80'
          }`}
        >
          {isSpeaking ? <VolumeX className="h-3.5 w-3.5" /> : <Volume2 className="h-3.5 w-3.5" />}
          <span>{isSpeaking ? 'Stop' : 'Speak'}</span>
        </button>

        {/* Notification Button & Dropdown */}
        <div className="relative">
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            aria-label="System notifications"
            className="h-8 w-8 rounded-full bg-bg-raised hover:bg-border-subtle flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors relative border border-border-subtle"
          >
            <Bell className="h-4 w-4" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-accent-500" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-bg-surface border border-border-subtle rounded-xl p-4 shadow-xl z-50">
              <div className="flex items-center justify-between pb-2.5 border-b border-border-subtle mb-3">
                <span className="text-xs font-bold text-text-primary tracking-wider uppercase">Notifications</span>
                <button onClick={() => setShowNotifications(false)} className="text-text-muted hover:text-text-primary">
                  <X className="h-4 w-4" />
                </button>
              </div>
              <div className="space-y-2.5">
                <div className="p-3 rounded-lg bg-accent-lavender/50 dark:bg-accent-950/40 border border-accent-200 dark:border-accent-800 text-xs">
                  <div className="flex items-center gap-1.5 text-accent-700 dark:text-accent-300 font-bold mb-1">
                    <CheckCircle2 className="h-3.5 w-3.5 text-accent-500" />
                    <span>AutoScientist LoRA Ready</span>
                  </div>
                  <p className="text-[11px] text-text-secondary">Experiment 819874ef verified on disk. Hybrid Core active.</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-base border border-border-subtle text-xs">
                  <span className="text-text-primary font-bold block mb-0.5">Spaced Repetition Check</span>
                  <p className="text-[11px] text-text-secondary">Transfer review scheduled for Quadratic Vertex today.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
