import axios from 'axios';
import { Question } from '../store/gameStore';

const API_BASE = process.env.EXPO_PUBLIC_BACKEND_URL || '';

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 30000,
});

export interface ScoreData {
  user_name: string;
  score: number;
  total_questions: number;
  correct_answers: number;
  difficulty: string;
  mode: string;
  language: string;
}

export interface LeaderboardEntry {
  rank: number;
  user_name: string;
  score: number;
  estimated_iq: number;
  difficulty: string;
  mode: string;
  date: string;
}

export const apiService = {
  // Initialize questions in database
  initQuestions: async () => {
    const response = await api.post('/init-questions');
    return response.data;
  },

  // Get questions
  getQuestions: async (
    difficulty?: string,
    category?: string,
    language: string = 'en',
    limit: number = 10
  ): Promise<Question[]> => {
    const params: Record<string, string | number> = { language, limit };
    if (difficulty) params.difficulty = difficulty;
    if (category) params.category = category;
    
    const response = await api.get('/questions', { params });
    return response.data;
  },

  // Submit score
  submitScore: async (scoreData: ScoreData) => {
    const response = await api.post('/scores', scoreData);
    return response.data;
  },

  // Get leaderboard
  getLeaderboard: async (
    mode?: string,
    difficulty?: string,
    limit: number = 20
  ): Promise<LeaderboardEntry[]> => {
    const params: Record<string, string | number> = { limit };
    if (mode) params.mode = mode;
    if (difficulty) params.difficulty = difficulty;
    
    const response = await api.get('/scores/leaderboard', { params });
    return response.data;
  },

  // Get daily challenge
  getDailyChallenge: async (language: string = 'en') => {
    const response = await api.get('/daily-challenge', {
      params: { language },
    });
    return response.data;
  },

  // Complete daily challenge
  completeDailyChallenge: async () => {
    const response = await api.post('/daily-challenge/complete');
    return response.data;
  },

  // Generate AI question
  generateAIQuestion: async (
    language: string,
    difficulty: string,
    category?: string
  ): Promise<Question> => {
    const response = await api.post('/generate-question', {
      language,
      difficulty,
      category,
    });
    return response.data;
  },
};
