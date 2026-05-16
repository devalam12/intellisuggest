export type Domain = 'movies' | 'books' | 'careers' | 'restaurants';

export interface DomainOption {
  id: Domain;
  label: string;
  icon: string;
  desc: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface Recommendation {
  title: string;
  match_score: number;
  why_youll_love_it: string;
  key_matches: string[];
  potential_caveat: string | null;
  vibe_tags: string[];
}

export interface RecommendationResponse {
  recommendations: Recommendation[];
  recommendation_rationale: string;
}

export interface UserPreferences {
  domain: string;
  [key: string]: unknown;
  confidence: number;
}

export type AppPhase = 'select' | 'chat' | 'results';
