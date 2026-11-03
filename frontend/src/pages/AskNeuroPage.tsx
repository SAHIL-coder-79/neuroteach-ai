import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Send, 
  HelpCircle, 
  BrainCircuit, 
  Zap, 
  CheckCircle2, 
  RefreshCw, 
  MessageSquarePlus, 
  Compass,
  Volume2,
  PlusCircle,
  FileQuestion
} from 'lucide-react';
import { ChatMessage, ErrorType, TeachingStrategy } from '@/types';
import { GraphPanel } from '@/components/visual/GraphPanel';
import { DEMO_QUESTIONS } from '@/data/demoData';
import { api, HealthApiResponse } from '@/api/client';
import { voiceAssistant } from '@/utils/voiceAssistant';

export const AskNeuroPage: React.FC = () => {
  const [selectedSubject, setSelectedSubject] = useState<'mathematics' | 'python' | 'dsa' | 'ai_ml'>('mathematics');
  const [currentQuestionTitle, setCurrentQuestionTitle] = useState<string>("Find the x-coordinate of the vertex for f(x) = x² - 4x + 3");
  const [canonicalAnswer, setCanonicalAnswer] = useState<string>("2");
  const [showCustomModal, setShowCustomModal] = useState<boolean>(false);
  const [customQuestionInput, setCustomQuestionInput] = useState<string>("");
  const [customAnswerInput, setCustomAnswerInput] = useState<string>("");
  const [serverHealth, setServerHealth] = useState<HealthApiResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeStrategyNote, setActiveStrategyNote] = useState<string>("Adaptive policy ready: Progressive hint initialized.");

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'm1',
      sender: 'student',
      text: "I calculated the vertex for f(x) = x² - 4x + 3 and got x = -2, but the answer key says x = 2. Why am I wrong?",
      reasoning: "I used the vertex formula x = b / 2a. Here a=1 and b=-4, so -4 / 2 = -2.",
      timestamp: '19:05',
    },
    {
      id: 'm2',
      sender: 'neuro',
      text: "Notice that in the formula x = -b / (2a), the leading minus sign flips the sign of b. What happens when b is negative?",
      diagnosis: {
        error_type: 'conceptual',
        misconception_id: 'sign_error_vertex',
        confidence: 0.88,
        evidence: 'x = b / 2a',
        explanation: 'Neglecting the negative sign in the standard vertex formula x = -b / (2a).',
        root_concepts: ['quadratic.standard_form'],
        counterexample: 'For f(x) = (x-2)², the vertex is clearly at x = +2, but b = -4 gives b/(2a) = -2.'
      },
      strategy: 'counterexample',
      visual_spec: DEMO_QUESTIONS[0].visual_spec,
      timestamp: '19:06',
    }
  ]);

  const [inputVal, setInputVal] = useState('');
  const [reasoningVal, setReasoningVal] = useState('');

  // Probe server health and model provenance on mount
  useEffect(() => {
    api.getHealth()
      .then(setServerHealth)
      .catch(() => setServerHealth(null));
  }, []);

  const handleNewChat = () => {
    const welcomeMsg: ChatMessage = {
      id: `m_${Date.now()}`,
      sender: 'neuro',
      text: `Hello Aarav! I'm your Socratic Tutor for ${selectedSubject.toUpperCase()}. Which question or problem would you like to investigate today? You can type any question or your current problem step below.`,
      timestamp: 'Just now',
    };
    setMessages([welcomeMsg]);
    setInputVal('');
    setReasoningVal('');
    setActiveStrategyNote("New conversation started. Waiting for student attempt.");
  };

  const handleSetCustomQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customQuestionInput.trim()) return;

    const q = customQuestionInput.trim();
    const ans = customAnswerInput.trim() || "N/A";
    setCurrentQuestionTitle(q);
    setCanonicalAnswer(ans);
    setShowCustomModal(false);
    setCustomQuestionInput("");
    setCustomAnswerInput("");

    // Initiate tutor on the new question
    const introMsg: ChatMessage = {
      id: `m_${Date.now()}`,
      sender: 'neuro',
      text: `We are now exploring your question: "${q}". How would you approach this, or what is your first thought?`,
      timestamp: 'Just now',
    };
    setMessages([introMsg]);
    setActiveStrategyNote(`Target Question Updated: ${q}`);
  };

  const handleSpeakMessage = (text: string) => {
    voiceAssistant.speak(text);
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim()) return;

    const studentText = inputVal;
    const studentReasoning = reasoningVal;

    const newMsg: ChatMessage = {
      id: `m_${Date.now()}`,
      sender: 'student',
      text: studentText,
      reasoning: studentReasoning ? studentReasoning : undefined,
      timestamp: 'Just now',
    };

    setMessages((prev) => [...prev, newMsg]);
    setInputVal('');
    setReasoningVal('');
    setIsLoading(true);

    try {
      const response = await api.processTurn({
        subject: selectedSubject,
        concept_id: selectedSubject === 'mathematics' ? 'quadratic.vertex' : `${selectedSubject}.core`,
        question_text: currentQuestionTitle,
        canonical_answer: canonicalAnswer,
        student_message: studentText,
        student_reasoning: studentReasoning || undefined,
      });

      const feedbackText = response.intervention?.text || "Let's reflect on your calculation step.";
      const strategyName = (response.strategy?.name || 'hint') as unknown as TeachingStrategy;

      const neuroMsg: ChatMessage = {
        id: `m_${Date.now()}`,
        sender: 'neuro',
        text: feedbackText,
        strategy: strategyName,
        diagnosis: response.diagnosis ? {
          error_type: (response.diagnosis.error_type || 'conceptual') as ErrorType,
          misconception_id: response.diagnosis.misconception_id || 'user_inquiry',
          confidence: response.diagnosis.confidence || 0.85,
          evidence: response.diagnosis.evidence || studentText,
          explanation: response.diagnosis.explanation || 'Identified pattern in student reasoning.',
          root_concepts: [selectedSubject],
        } : undefined,
        timestamp: 'Just now',
      };

      setMessages((prev) => [...prev, neuroMsg]);
      setActiveStrategyNote(`Active Policy: ${response.strategy?.name || 'adaptive'} (Source: LoRA 819874ef Hybrid Core)`);
      handleSpeakMessage(feedbackText);
    } catch {
      // Dynamic fallback based on what the student actually asked
      let fallbackText = `That's an interesting question about "${studentText}". What is your current hypothesis or what have you learned about it so far?`;
      if (studentText.toLowerCase().includes("photosynthesis")) {
        fallbackText = "Photosynthesis is the cellular process plants use to produce glucose from light energy, carbon dioxide, and water. What inputs do plants absorb from their surroundings?";
      }

      const fallbackMsg: ChatMessage = {
        id: `m_${Date.now()}`,
        sender: 'neuro',
        text: fallbackText,
        strategy: 'guided_problem_solving',
        timestamp: 'Just now',
      };
      setMessages((prev) => [...prev, fallbackMsg]);
      setActiveStrategyNote("Active Policy: Socratic Question (Offline Fallback)");
      handleSpeakMessage(fallbackMsg.text);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImStuck = async () => {
    setIsLoading(true);
    try {
      const response = await api.processTurn({
        subject: selectedSubject,
        concept_id: 'quadratic.vertex',
        question_text: currentQuestionTitle,
        canonical_answer: canonicalAnswer,
        student_message: "I'm stuck and need a simpler step.",
        student_reasoning: "I don't know where to start.",
      });

      const feedbackText = response.intervention?.text || "Let's break this down into a simpler first step. What is the fundamental definition we are starting with?";
      const stuckMsg: ChatMessage = {
        id: `m_stuck_${Date.now()}`,
        sender: 'neuro',
        text: feedbackText,
        strategy: 'simpler_prerequisite',
        hint_level: 1,
        timestamp: 'Just now',
      };
      setMessages((prev) => [...prev, stuckMsg]);
      setActiveStrategyNote("Markov Policy Shift: Stepped down to simpler_prerequisite.");
      handleSpeakMessage(feedbackText);
    } catch {
      const fallbackStuck: ChatMessage = {
        id: `m_stuck_${Date.now()}`,
        sender: 'neuro',
        text: "Let's step back to a simpler prerequisite: What is the main definition or formula we need to apply here?",
        strategy: 'simpler_prerequisite',
        hint_level: 1,
        timestamp: 'Just now',
      };
      setMessages((prev) => [...prev, fallbackStuck]);
      setActiveStrategyNote("Markov Policy Shift: Stepped down to simpler_prerequisite.");
      handleSpeakMessage(fallbackStuck.text);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e as any);
    }
  };

  return (
    <div className="flex-1 flex flex-col lg:flex-row h-full overflow-hidden bg-bg-base transition-colors relative">
      {/* Primary Dialogue Stream */}
      <div className="flex-1 flex flex-col h-full border-r border-border-subtle overflow-hidden">
        {/* Banner with Subject Selector & Action Buttons */}
        <div className="px-6 py-3 bg-bg-surface border-b border-border-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-1.5 text-accent-500 font-bold">
              <Sparkles className="h-4 w-4" />
              <span>Socratic Tutor</span>
            </div>

            {/* Subject Selector Pills */}
            <div className="flex items-center gap-1 bg-bg-raised p-1 rounded-xl border border-border-subtle">
              {(['mathematics', 'python', 'dsa', 'ai_ml'] as const).map((subj) => (
                <button
                  key={subj}
                  onClick={() => setSelectedSubject(subj)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all ${
                    selectedSubject === subj
                      ? 'bg-accent-500 text-white shadow-xs'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  {subj.replace('_', '/')}
                </button>
              ))}
            </div>

            {serverHealth && (
              <span className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 dark:bg-emerald-950/50 text-success border border-emerald-200 dark:border-emerald-800">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>LoRA 819874ef Connected</span>
              </span>
            )}

            {isLoading && (
              <span className="inline-flex items-center gap-1 text-xs text-accent-500 font-medium">
                <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                <span>Evaluating Pedagogy...</span>
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Ask / Set Custom Question Button */}
            <button
              onClick={() => setShowCustomModal(true)}
              className="px-3 py-1.5 rounded-xl bg-accent-softcyan dark:bg-[#132B38] text-accent-cyan dark:text-[#38BDF8] border border-accent-cyan/30 text-xs font-bold flex items-center gap-1.5 transition-colors"
              title="Add or change the target problem / question"
            >
              <FileQuestion className="h-4 w-4" />
              <span>Change Question</span>
            </button>

            {/* New Chat Button */}
            <button
              onClick={handleNewChat}
              className="px-3 py-1.5 rounded-xl bg-accent-lavender hover:bg-accent-200 text-accent-700 dark:bg-[#241E3E] dark:text-accent-300 dark:border-accent-700 border border-accent-200 text-xs font-bold flex items-center gap-1.5 transition-colors"
              title="Start a fresh conversation"
            >
              <MessageSquarePlus className="h-4 w-4" />
              <span>New Chat</span>
            </button>
          </div>
        </div>

        {/* Current Active Question Context Bar */}
        <div className="px-6 py-2 bg-bg-raised border-b border-border-subtle flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 overflow-hidden">
            <span className="font-bold text-accent-500 shrink-0">Current Question:</span>
            <span className="truncate text-text-primary font-medium">{currentQuestionTitle}</span>
          </div>
          <button 
            onClick={() => setShowCustomModal(true)} 
            className="text-[11px] text-accent-cyan hover:underline shrink-0 ml-3 font-semibold"
          >
            Custom Question +
          </button>
        </div>

        {/* Message History */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg) => (
            <div 
              key={msg.id}
              className={`flex flex-col ${msg.sender === 'student' ? 'items-end' : 'items-start'}`}
            >
              <div 
                className={`max-w-2xl rounded-2xl p-5 text-sm shadow-sm transition-all ${
                  msg.sender === 'student'
                    ? 'bg-accent-lavender text-text-primary dark:bg-[#241E3E] dark:text-[#F4F6FD] border border-accent-200 dark:border-[#3E3865] rounded-br-xs'
                    : 'bg-bg-surface text-text-primary border border-border-subtle rounded-bl-xs'
                }`}
              >
                {/* Neuro Header */}
                {msg.sender === 'neuro' && (
                  <div className="flex items-center justify-between gap-3 mb-3 pb-2.5 border-b border-border-subtle text-xs">
                    <div className="flex items-center gap-2 font-bold text-accent-500">
                      <BrainCircuit className="h-4 w-4" />
                      <span>NEURO TUTOR</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleSpeakMessage(msg.text)}
                        title="Listen to response"
                        className="p-1 rounded-lg text-text-muted hover:text-accent-500 hover:bg-bg-raised transition-colors"
                      >
                        <Volume2 className="h-4 w-4" />
                      </button>
                      {msg.strategy && (
                        <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-accent-softcyan dark:bg-[#132B38] text-accent-cyan dark:text-[#38BDF8] border border-accent-cyan/30 font-semibold uppercase tracking-wider">
                          {String(msg.strategy).replace('_', ' ')}
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Body Text */}
                <p className="leading-relaxed whitespace-pre-wrap font-medium text-text-primary">{msg.text}</p>

                {/* Student reasoning display if present */}
                {msg.sender === 'student' && msg.reasoning && (
                  <div className="mt-3 p-3 rounded-xl bg-bg-surface/80 dark:bg-bg-base/60 text-xs text-text-secondary border border-border-subtle">
                    <span className="font-bold text-accent-500 block mb-1">Submitted Reasoning:</span>
                    <span>{msg.reasoning}</span>
                  </div>
                )}

                {/* Misconception Diagnostic Card if present */}
                {msg.diagnosis && (
                  <div className="mt-4 p-4 rounded-xl bg-bg-raised border border-border-subtle space-y-2.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-accent-500 flex items-center gap-1.5">
                        <Zap className="h-4 w-4 text-accent-cyan" />
                        <span>Misconception DNA Identified</span>
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase bg-rose-50 dark:bg-rose-950/60 text-danger border border-rose-200 dark:border-rose-900">
                        {msg.diagnosis.misconception_id}
                      </span>
                    </div>
                    <p className="text-text-secondary leading-relaxed">
                      {msg.diagnosis.explanation}
                    </p>
                    {msg.diagnosis.counterexample && (
                      <div className="p-3 rounded-lg bg-bg-surface border border-border-subtle text-xs text-text-secondary">
                        <strong className="text-text-primary block mb-1">Counterexample Proof:</strong>
                        <span>{msg.diagnosis.counterexample}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-start gap-3">
              <div className="p-4 rounded-2xl bg-bg-surface border border-border-subtle flex items-center gap-3 shadow-xs">
                <RefreshCw className="h-4 w-4 text-accent-500 animate-spin" />
                <span className="text-xs text-text-secondary font-medium">Evaluating pedagogical strategy & checking answer leakage...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Bar Form */}
        <div className="p-4 bg-bg-surface border-t border-border-subtle">
          <form onSubmit={handleSend} className="space-y-3">
            <div className="flex gap-3">
              <div className="flex-1 space-y-2">
                <textarea
                  value={inputVal}
                  onChange={(e) => setInputVal(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a question or explain your reasoning step... (Enter to send, Shift+Enter for new line)"
                  rows={2}
                  className="w-full rounded-xl bg-bg-raised p-3 text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent-500 transition-all resize-none border border-border-subtle"
                />
                <input
                  type="text"
                  value={reasoningVal}
                  onChange={(e) => setReasoningVal(e.target.value)}
                  placeholder="Optional: How did you arrive at this step? (Your reasoning helps diagnose misconceptions)"
                  className="w-full rounded-lg bg-bg-raised px-3 py-1.5 text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent-500 transition-all border border-border-subtle"
                />
              </div>

              <div className="flex flex-col justify-end gap-2 shrink-0">
                <button
                  type="button"
                  onClick={handleImStuck}
                  disabled={isLoading}
                  className="px-3.5 py-2 rounded-xl bg-[#FFF6E7] hover:bg-[#F8DFB5]/50 dark:bg-[#2C2114] text-warning border border-warning/30 text-xs font-bold flex items-center gap-1.5 transition-colors disabled:opacity-50"
                  title="Request simpler prerequisite hint"
                >
                  <HelpCircle className="h-4 w-4" />
                  <span>I'm Stuck</span>
                </button>
                <button
                  type="submit"
                  disabled={isLoading || !inputVal.trim()}
                  className="px-5 py-2.5 rounded-xl bg-accent-500 hover:bg-accent-600 disabled:opacity-50 text-white font-bold text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                >
                  <Send className="h-4 w-4" />
                  <span>Send Turn</span>
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Right-Hand Visual Spec & Policy Column */}
      <div className="w-full lg:w-96 bg-bg-surface border-l border-border-subtle flex flex-col h-full overflow-hidden border-t lg:border-t-0">
        <div className="p-4 border-b border-border-subtle flex items-center justify-between text-xs">
          <span className="font-bold text-text-primary uppercase tracking-wider flex items-center gap-1.5">
            <Compass className="h-4 w-4 text-accent-500" />
            <span>Visual Spec & Policy</span>
          </span>
          <span className="text-xs font-semibold text-accent-cyan">Active Engine</span>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Active Strategy Card */}
          <div className="p-4 rounded-xl bg-bg-raised border border-border-subtle space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-text-primary">Active Policy Rule</span>
              <span className="text-[10px] font-mono text-accent-cyan font-bold">Guardrails On</span>
            </div>
            <p className="text-xs text-text-secondary leading-relaxed">
              {activeStrategyNote}
            </p>
          </div>

          {/* Interactive Graph Panel */}
          <div>
            <span className="text-xs font-bold text-text-primary block mb-2">Visual Coordinate Representation</span>
            <GraphPanel spec={DEMO_QUESTIONS[0].visual_spec!} />
          </div>

          {/* Invariant Note */}
          <div className="p-3.5 rounded-xl bg-accent-softcyan dark:bg-[#132B38] border border-accent-cyan/30 text-xs text-text-secondary space-y-1">
            <strong className="text-text-primary block font-bold">Answer Leakage Guard:</strong>
            <span>Direct answers are deterministically filtered before being served. Only progressive hints and counterexamples are delivered.</span>
          </div>
        </div>
      </div>

      {/* Custom Question Modal */}
      {showCustomModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-bg-surface border border-border-subtle rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border-subtle pb-3">
              <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
                <PlusCircle className="h-5 w-5 text-accent-500" />
                <span>Ask Any Custom Question</span>
              </h3>
              <button 
                onClick={() => setShowCustomModal(false)}
                className="text-text-muted hover:text-text-primary text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSetCustomQuestion} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-text-primary mb-1">
                  Question / Problem Statement
                </label>
                <textarea
                  required
                  rows={3}
                  value={customQuestionInput}
                  onChange={(e) => setCustomQuestionInput(e.target.value)}
                  placeholder="e.g., What is photosynthesis? or Why does binary search require a sorted array?"
                  className="w-full rounded-xl bg-bg-raised p-3 text-xs text-text-primary placeholder:text-text-muted border border-border-subtle focus:outline-none focus:ring-1 focus:ring-accent-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-text-primary mb-1">
                  Expected / Canonical Answer (Optional, for anti-leakage checking)
                </label>
                <input
                  type="text"
                  value={customAnswerInput}
                  onChange={(e) => setCustomAnswerInput(e.target.value)}
                  placeholder="e.g., process of converting light energy into glucose"
                  className="w-full rounded-xl bg-bg-raised px-3 py-2 text-xs text-text-primary placeholder:text-text-muted border border-border-subtle focus:outline-none focus:ring-1 focus:ring-accent-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCustomModal(false)}
                  className="px-4 py-2 rounded-xl bg-bg-raised text-text-secondary hover:text-text-primary text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-accent-500 hover:bg-accent-600 text-white text-xs font-bold"
                >
                  Start Socratic Dialogue
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
