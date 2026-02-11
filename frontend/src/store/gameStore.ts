import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Language } from '../i18n/translations';

export type Difficulty = 'easy' | 'medium' | 'hard';
export type GameMode = 'classic' | 'time_race' | 'daily' | 'multiplayer';

export interface Question {
  id: string;
  category: string;
  difficulty: string;
  question: string;
  options: string[];
  correct_answer: number;
}

interface GameState {
  language: Language;
  playerName: string;
  currentScore: number;
  currentQuestion: number;
  totalQuestions: number;
  correctAnswers: number;
  difficulty: Difficulty;
  gameMode: GameMode;
  questions: Question[];
  timeLeft: number;
  timeBonus: number;
  isGameActive: boolean;
  showAd: boolean;
  adCounter: number;
  
  // Actions
  setLanguage: (lang: Language) => void;
  setPlayerName: (name: string) => void;
  setDifficulty: (diff: Difficulty) => void;
  setGameMode: (mode: GameMode) => void;
  setQuestions: (questions: Question[]) => void;
  answerQuestion: (isCorrect: boolean, points: number) => void;
  nextQuestion: () => void;
  addTimeBonus: (seconds: number) => void;
  decrementTime: () => void;
  setTimeLeft: (time: number) => void;
  resetGame: () => void;
  startGame: () => void;
  endGame: () => void;
  triggerAd: () => void;
  closeAd: () => void;
}

export const useGameStore = create<GameState>()(
  persist(
    (set, get) => ({
      language: 'en',
      playerName: '',
      currentScore: 0,
      currentQuestion: 0,
      totalQuestions: 10,
      correctAnswers: 0,
      difficulty: 'easy',
      gameMode: 'classic',
      questions: [],
      timeLeft: 60,
      timeBonus: 0,
      isGameActive: false,
      showAd: false,
      adCounter: 0,

      setLanguage: (lang) => set({ language: lang }),
      setPlayerName: (name) => set({ playerName: name }),
      setDifficulty: (diff) => set({ difficulty: diff }),
      setGameMode: (mode) => set({ gameMode: mode }),
      setQuestions: (questions) => set({ questions, totalQuestions: questions.length }),
      
      answerQuestion: (isCorrect, points) => set((state) => ({
        currentScore: isCorrect ? state.currentScore + points : state.currentScore,
        correctAnswers: isCorrect ? state.correctAnswers + 1 : state.correctAnswers,
      })),
      
      nextQuestion: () => {
        const state = get();
        const newQuestionNumber = state.currentQuestion + 1;
        const newAdCounter = state.adCounter + 1;
        
        // Show ad every 5 questions
        if (newAdCounter >= 5 && newQuestionNumber < state.totalQuestions) {
          set({ 
            currentQuestion: newQuestionNumber, 
            adCounter: 0,
            showAd: true 
          });
        } else {
          set({ 
            currentQuestion: newQuestionNumber, 
            adCounter: newAdCounter 
          });
        }
      },
      
      addTimeBonus: (seconds) => set((state) => ({
        timeLeft: state.timeLeft + seconds,
        timeBonus: state.timeBonus + seconds,
      })),
      
      decrementTime: () => set((state) => ({
        timeLeft: Math.max(0, state.timeLeft - 1),
      })),
      
      setTimeLeft: (time) => set({ timeLeft: time }),
      
      resetGame: () => set({
        currentScore: 0,
        currentQuestion: 0,
        correctAnswers: 0,
        questions: [],
        timeLeft: 60,
        timeBonus: 0,
        isGameActive: false,
        showAd: false,
        adCounter: 0,
      }),
      
      startGame: () => set({ isGameActive: true }),
      endGame: () => set({ isGameActive: false }),
      
      triggerAd: () => set({ showAd: true }),
      closeAd: () => set({ showAd: false }),
    }),
    {
      name: 'iq-game-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        language: state.language,
        playerName: state.playerName,
      }),
    }
  )
);
