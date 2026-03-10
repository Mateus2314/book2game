// Mock fixtures for testing
export const mockUsers = {
  user1: {
    id: '1',
    email: 'test@example.com',
    username: 'testuser',
    name: 'Test User',
    avatar_url: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  user2: {
    id: '2',
    email: 'user2@example.com',
    username: 'user2',
    name: 'User Two',
    avatar_url: 'https://example.com/avatar.jpg',
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
};

export const mockBooks = {
  book1: {
    id: '1',
    title: 'The Great Gatsby',
    authors: ['F. Scott Fitzgerald'],
    description: 'A novel of the Jazz Age',
    google_books_id: 'gcQrAAAAMAAJ',
    isbn_10: '0743273567',
    isbn_13: '978-0743273565',
    published_date: '1925-04-10',
    publisher: 'Scribner',
    page_count: 180,
    language: 'en',
    categories: ['Fiction', 'Classic'],
    cover_image_url: 'https://example.com/cover.jpg',
    created_at: '2024-01-01T00:00:00Z',
  },
  book2: {
    id: '2',
    title: '1984',
    authors: ['George Orwell'],
    description: 'A dystopian novel',
    google_books_id: 'KjwUPC9syK4C',
    isbn_10: '0451524934',
    isbn_13: '978-0451524935',
    published_date: '1949-06-08',
    publisher: 'Penguin Books',
    page_count: 328,
    language: 'en',
    categories: ['Fiction', 'Dystopian', 'Science Fiction'],
    cover_image_url: 'https://example.com/1984.jpg',
    created_at: '2024-01-02T00:00:00Z',
  },
};

export const mockGames = {
  game1: {
    id: '1',
    name: 'The Witcher 3: Wild Hunt',
    genres: ['RPG', 'Adventure'],
    rating: 9.3,
    metacritic: 92,
    description: 'An open-world RPG with an immersive story',
    released: '2015-05-19',
    developers: ['CD Projekt Red'],
    platforms: ['PC', 'PlayStation', 'Xbox'],
  },
  game2: {
    id: '2',
    name: 'Elden Ring',
    genres: ['RPG', 'Action'],
    rating: 9.0,
    metacritic: 96,
    description: 'A challenging action RPG',
    released: '2022-02-25',
    developers: ['FromSoftware'],
    platforms: ['PC', 'PlayStation', 'Xbox'],
  },
};

export const mockRecommendations = {
  rec1: {
    id: '1',
    user_id: '1',
    book_id: '1',
    game_ids: ['1', '2'],
    similarity_scores: { '1': 0.95, '2': 0.87 },
    reasoning: 'Based on similar themes and genres',
    created_at: '2024-01-01T00:00:00Z',
  },
};

export const mockUserBooks = {
  ub1: {
    id: '1',
    user_id: '1',
    book_id: '1',
    book: mockBooks.book1,
    added_at: '2024-01-01T00:00:00Z',
    rating: 5,
    review: 'Great book!',
  },
};

export const mockUserGames = {
  ug1: {
    id: '1',
    user_id: '1',
    game_id: '1',
    game: mockGames.game1,
    added_at: '2024-01-01T00:00:00Z',
    hours_played: 120,
    rating: 5,
    review: 'Amazing game!',
  },
};

// Helper to create custom mocks
export const createMockBook = (overrides = {}): any => ({
  ...mockBooks.book1,
  ...overrides,
});

export const createMockGame = (overrides = {}): any => ({
  ...mockGames.game1,
  ...overrides,
});

export const createMockUser = (overrides = {}): any => ({
  ...mockUsers.user1,
  ...overrides,
});

export const createMockRecommendation = (overrides = {}): any => ({
  ...mockRecommendations.rec1,
  ...overrides,
});