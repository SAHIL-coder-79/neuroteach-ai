/**
 * Browser-Native Web Speech API Utility for NeuroTeach AI
 * Provides instant Text-to-Speech (TTS) voice assistance without external paid services.
 */

class VoiceAssistantService {
  private synth: SpeechSynthesis | null = null;
  private isSpeakingState = false;
  private listeners: ((speaking: boolean) => void)[] = [];

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
    }
  }

  public isSupported(): boolean {
    return this.synth !== null;
  }

  public subscribe(callback: (speaking: boolean) => void): () => void {
    this.listeners.push(callback);
    callback(this.isSpeakingState);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  private notify(speaking: boolean) {
    this.isSpeakingState = speaking;
    this.listeners.forEach(cb => cb(speaking));
  }

  /**
   * Speak text clearly using natural English speech synthesis.
   */
  public speak(text: string, onEnd?: () => void) {
    if (!this.synth) {
      console.warn('Speech synthesis not supported in this browser.');
      return;
    }

    // Stop any ongoing speech
    this.stop();

    // Clean markdown/latex formatting symbols for natural voice output
    const cleanText = text
      .replace(/\$\$(.*?)\$\$/g, '$1')
      .replace(/\$(.*?)\$/g, '$1')
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/`([^`]+)`/g, '$1')
      .replace(/#+\s/g, '')
      .replace(/\n+/g, ' ')
      .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.05;

    // Pick a smooth natural English voice if available
    const voices = this.synth.getVoices();
    const naturalVoice = voices.find(v => 
      (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('Jenny') || v.name.includes('Guy')) &&
      v.lang.startsWith('en')
    ) || voices.find(v => v.lang.startsWith('en'));

    if (naturalVoice) {
      utterance.voice = naturalVoice;
    }

    utterance.onstart = () => {
      this.notify(true);
    };

    utterance.onend = () => {
      this.notify(false);
      if (onEnd) onEnd();
    };

    utterance.onerror = (e) => {
      console.warn('Speech synthesis utterance error:', e);
      this.notify(false);
    };

    this.synth.speak(utterance);
  }

  /**
   * Extract meaningful text from visible main content on the screen and speak it.
   */
  public speakScreen() {
    const mainEl = document.querySelector('main');
    if (!mainEl) {
      this.speak("Welcome to NeuroTeach AI, your adaptive Socratic learning companion.");
      return;
    }
    // Collect text from headings and paragraphs in view
    const elements = Array.from(mainEl.querySelectorAll('h1, h2, h3, h4, p'));
    const combinedText = elements
      .slice(0, 8)
      .map(el => (el as HTMLElement).innerText.trim())
      .filter(t => t.length > 0)
      .join('. ');

    if (combinedText) {
      this.speak(combinedText);
    } else {
      this.speak("Welcome to NeuroTeach AI. No readable text found in active view.");
    }
  }

  public stop() {
    if (this.synth) {
      this.synth.cancel();
      this.notify(false);
    }
  }

  public toggle(text: string) {
    if (this.isSpeakingState) {
      this.stop();
    } else {
      this.speak(text);
    }
  }

  public isSpeaking(): boolean {
    return this.isSpeakingState;
  }
}

export const voiceAssistant = new VoiceAssistantService();
