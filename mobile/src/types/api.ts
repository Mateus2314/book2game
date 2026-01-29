// Auth types
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

// Book types
export interface Book {
  id: number;
  google_books_id: string;
  title: string;
  authors?: string[] | string;
  publisher?: string;
  published_date?: string;
  description?: string;
  isbn_10?: string;
  isbn_13?: string;
  page_count?: number;
  categories?: string[] | string;
  language: string;
  image_url?: string;
  preview_link?: string;
  created_at: string;
  updated_at: string;
}

export interface BookSearchResponse {
  items: Book[];
  total: number;
  page: number;
  per_page: number;
}

// Game types
export interface Game {
  id: number;
  rawg_id: number;
  name: string;
  slug: string;
  description?: string;
  released?: string;
  rating?: number;
  ratings_count?: number;
  metacritic?: number;
  playtime?: number;
  genres?: string[];
  tags?: string[];
  platforms?: string[];
  developers?: string[];
  publishers?: string[];
  image_url?: string;
  website?: string;
  created_at: string;
  updated_at: string;
}

// Recommendation types
export interface RecommendationGame {
  game_id: number;
  score: number;
}

export interface Recommendation {
  id: number;
  user_id: number;
  book_id: number;
  games: RecommendationGame[];
  recommended_games?: RecommendationGame[];
  ai_generated: boolean;
  similarity_score: number;
  processing_time_ms: number;
  created_at: string;
  updated_at: string;
  book?: Book;
  game_details?: Game[];
}

export interface CreateRecommendationRequest {
  book_id?: number;
}

// Library types
export type ReadingStatus = 'to_read' | 'reading' | 'finished';
export type PlayStatus = 'to_play' | 'playing' | 'completed';

export interface UserBook {
  id: number;
  user_id: number;
  book_id: number;
  is_favorite: boolean;
  reading_status: ReadingStatus;
  personal_rating?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  book?: Book;
}

export interface UserGame {
  id: number;
  user_id: number;
  game_id: number;
  is_favorite: boolean;
  play_status: PlayStatus;
  personal_rating?: number;
  notes?: string;
  hours_played?: number;
  created_at: string;
  updated_at: string;
  game?: Game;
}

export interface AddBookToLibraryRequest {
  google_books_id: string;
  is_favorite?: boolean;
  reading_status?: ReadingStatus;
  personal_rating?: number;
  notes?: string;
}

export interface AddGameToLibraryRequest {
  game_id: number;
  is_favorite?: boolean;
  play_status?: PlayStatus;
  personal_rating?: number;
  notes?: string;
  hours_played?: number;
}

export interface UpdateBookMetadataRequest {
  is_favorite?: boolean;
  reading_status?: ReadingStatus;
  personal_rating?: number;
  notes?: string;
}

export interface UpdateGameMetadataRequest {
  is_favorite?: boolean;
  play_status?: PlayStatus;
  personal_rating?: number;
  notes?: string;
  hours_played?: number;
}

// Error types
export type ApiError =
  | { detail: string; status?: number }
  | Array<{ loc: any; msg: string; type: string; input?: any; url?: string }>;
