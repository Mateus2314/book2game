import {api} from './axios';
import qs from 'qs';
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  BookSearchResponse,
  Book,
  CreateRecommendationRequest,
  Recommendation,
  Game,
  UserBook,
  UserGame,
  AddBookToLibraryRequest,
  AddGameToLibraryRequest,
  UpdateBookMetadataRequest,
  UpdateGameMetadataRequest,
  User,
} from '../../types/api';

// Auth endpoints
export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>(
    '/auth/login',
    qs.stringify(data), // transforma em x-www-form-urlencoded
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  );
  console.log('Login response data:', response);
  return response.data;
},

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  refresh: async (refreshToken: string): Promise<{access_token: string}> => {
    const response = await api.post<{access_token: string}>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },
};

// Books endpoints
export const booksApi = {
  search: async (
    query: string,
    page: number = 1,
  ): Promise<BookSearchResponse> => {
    const response = await api.get<BookSearchResponse>('/books/search', {
      params: {
        query, // termo de busca
        max_results: 10, // ou o valor desejado
        start_index: (page - 1) * 10, // para paginação correta
      },
    });
    return response.data;
  },

  getById: async (bookId: string): Promise<Book> => {
    const response = await api.get<Book>(`/books/${bookId}`);
    return response.data;
  },
};

// Recommendations endpoints
export const recommendationsApi = {
  create: async (
    data: CreateRecommendationRequest,
  ): Promise<Recommendation> => {
    const response = await api.post<Recommendation>('/recommendations', data);
    return response.data;
  },

  getAll: async (page: number = 1): Promise<Recommendation[]> => {
    const response = await api.get<Recommendation[]>('/recommendations', {
      params: {page},
    });
    return response.data;
  },

  getById: async (recommendationId: number): Promise<Recommendation> => {
    const response = await api.get<Recommendation>(
      `/recommendations/${recommendationId}`,
    );
    return response.data;
  },
};

// Games endpoints
export const gamesApi = {
  search: async (query: string, page: number = 1): Promise<Game[]> => {
    const response = await api.get<Game[]>('/games/search', {
      params: {q: query, page},
    });
    return response.data;
  },

  getById: async (gameId: number): Promise<Game> => {
    const response = await api.get<Game>(`/games/${gameId}`);
    return response.data;
  },

  searchByTags: async (tags: string[]): Promise<Game[]> => {
    const response = await api.get<Game[]>('/games/tags', {
      params: {tags: tags.join(',')},
    });
    return response.data;
  },
};

// Users endpoints
export const usersApi = {
  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/users/me');
    return response.data;
  },

  updateMe: async (data: Partial<User>): Promise<User> => {
    const response = await api.put<User>('/users/me', data);
    return response.data;
  },

  getMyRecommendations: async (page: number = 1): Promise<Recommendation[]> => {
    const me = await usersApi.getMe();
    const response = await api.get<Recommendation[]>(
      `/users/${me.id}/recommendations`,
      {params: {page}},
    );
    return response.data;
  },

  // Book library
  getBookLibrary: async (
    skip = 0,
    limit = 50,
  ): Promise<UserBook[]> => {
    const response = await api.get<UserBook[]>('/users/me/books', {
      params: {skip, limit},
    });
    return response.data;
  },

  addBookToLibrary: async (
    data: AddBookToLibraryRequest,
  ): Promise<UserBook> => {
    const response = await api.post<UserBook>(`/users/me/books/from-google/${data.google_books_id}`);
    return response.data;
  },

  addExistingBookToLibrary: async (bookId: number): Promise<UserBook> => {
    const response = await api.post<UserBook>(`/users/library/${bookId}`);
    return response.data;
  },

  updateBookMetadata: async (
    bookId: number,
    data: UpdateBookMetadataRequest,
  ): Promise<UserBook> => {
    const response = await api.put<UserBook>(`/users/library/${bookId}`, data);
    return response.data;
  },

  removeBookFromLibrary: async (bookId: number): Promise<void> => {
    await api.delete(`/users/library/${bookId}`);
  },

  // Game library
  getGameLibrary: async (
    favorite?: boolean,
    status?: string,
  ): Promise<UserGame[]> => {
    const response = await api.get<UserGame[]>('/users/game-library', {
      params: {favorite, status},
    });
    return response.data;
  },

  addGameToLibrary: async (
    data: AddGameToLibraryRequest,
  ): Promise<UserGame> => {
    const response = await api.post<UserGame>('/users/game-library', data);
    return response.data;
  },

  updateGameMetadata: async (
    gameId: number,
    data: UpdateGameMetadataRequest,
  ): Promise<UserGame> => {
    const response = await api.put<UserGame>(
      `/users/game-library/${gameId}`,
      data,
    );
    return response.data;
  },

  removeGameFromLibrary: async (gameId: number): Promise<void> => {
    await api.delete(`/users/game-library/${gameId}`);
  },
};
