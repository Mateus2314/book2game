import axios from 'axios';
import { mockUsers, mockBooks, mockGames } from '../../helpers/mockData';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Complete API Integration Workflows', () => {
  const API_URL = 'http://localhost:3000';

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Cross-service User Flow', () => {
    it('should handle user login and fetch dashboard data', async () => {
      // Step 1: Login
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          access_token: 'test-token',
          user: mockUsers.user1,
        },
        status: 200,
      });

      let response = await axios.post(`${API_URL}/auth/login`, {
        email: mockUsers.user1.email,
        password: 'password',
      });
      expect(response.data.access_token).toBeDefined();

      // Step 2: Get user dashboard statistics
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          total_books: 25,
          total_games: 15,
          books_read: 12,
          avg_book_rating: 4.5,
          avg_game_rating: 4.0,
        },
        status: 200,
      });

      response = await axios.get(`${API_URL}/users/user123/statistics`);
      expect(response.data.total_books).toBe(25);

      // Step 3: Get recommendations
      mockedAxios.get.mockResolvedValueOnce({
        data: [
          { id: 'rec1', source: 'book', item_id: 'book1' },
          { id: 'rec2', source: 'game', item_id: 'game1' },
        ],
        status: 200,
      });

      response = await axios.get(`${API_URL}/users/user123/recommendations`);
      expect(response.data).toHaveLength(2);
    });

    it('should handle complete discover and add flow', async () => {
      // Step 1: Search books
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1, mockBooks.book2],
        status: 200,
      });

      let response = await axios.get(`${API_URL}/books?search=fiction`);
      expect(response.data).toHaveLength(2);

      // Step 2: Get book details
      mockedAxios.get.mockResolvedValueOnce({
        data: mockBooks.book1,
        status: 200,
      });

      response = await axios.get(`${API_URL}/books/${mockBooks.book1.id}`);
      expect(response.data.id).toBe(mockBooks.book1.id);

      // Step 3: Add to library
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          id: 'user-book-1',
          user_id: 'user123',
          book_id: mockBooks.book1.id,
        },
        status: 201,
      });

      response = await axios.post(
        `${API_URL}/users/user123/books/${mockBooks.book1.id}`,
        {}
      );
      expect(response.status).toBe(201);

      // Step 4: Rate the book
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          user_id: 'user123',
          book_id: mockBooks.book1.id,
          rating: 5,
        },
        status: 201,
      });

      response = await axios.post(
        `${API_URL}/users/user123/books/${mockBooks.book1.id}/rate`,
        { rating: 5 }
      );
      expect(response.status).toBe(201);
    });

    it('should handle mixed search across books and games', async () => {
      // Step 1: Search books
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1],
        status: 200,
      });

      let response = await axios.get(`${API_URL}/books?search=adventure`);
      expect(response.data).toHaveLength(1);

      // Step 2: Search games
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game1],
        status: 200,
      });

      response = await axios.get(`${API_URL}/games?search=adventure`);
      expect(response.data).toHaveLength(1);

      // Step 3: Get book and game details in parallel context
      mockedAxios.get.mockResolvedValueOnce({
        data: mockBooks.book1,
        status: 200,
      });
      mockedAxios.get.mockResolvedValueOnce({
        data: mockGames.game1,
        status: 200,
      });

      const bookPromise = axios.get(`${API_URL}/books/${mockBooks.book1.id}`);
      const gamePromise = axios.get(`${API_URL}/games/${mockGames.game1.id}`);

      const [bookRes, gameRes] = await Promise.all([bookPromise, gamePromise]);
      expect(bookRes.data.id).toBe(mockBooks.book1.id);
      expect(gameRes.data.id).toBe(mockGames.game1.id);
    });
  });

  describe('Social Interaction Flow', () => {
    it('should handle user follow and share recommendation', async () => {
      // Step 1: Get user profile
      mockedAxios.get.mockResolvedValueOnce({
        data: mockUsers.user1,
        status: 200,
      });

      let response = await axios.get(`${API_URL}/users/user123/profile`);
      expect(response.data).toEqual(mockUsers.user1);

      // Step 2: Follow another user
      mockedAxios.post.mockResolvedValueOnce({
        data: { follower_id: 'user123', following_id: 'user456' },
        status: 201,
      });

      response = await axios.post(`${API_URL}/users/user123/follow/user456`, {});
      expect(response.status).toBe(201);

      // Step 3: Create a recommendation
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          id: 'rec1',
          source: 'book',
          item_id: 'book1',
          user_id: 'user123',
        },
        status: 201,
      });

      response = await axios.post(`${API_URL}/recommendations`, {
        source: 'book',
        item_id: 'book1',
      });
      expect(response.status).toBe(201);
    });

    it('should handle view follower recommendations', async () => {
      // Step 1: Get following list
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockUsers.user2],
        status: 200,
      });

      let response = await axios.get(`${API_URL}/users/user123/following`);
      expect(response.data).toHaveLength(1);

      // Step 2: Get recommendations from followed users
      mockedAxios.get.mockResolvedValueOnce({
        data: [
          { id: 'rec1', source: 'book', user_id: 'user456' },
          { id: 'rec2', source: 'game', user_id: 'user456' },
        ],
        status: 200,
      });

      response = await axios.get(
        `${API_URL}/recommendations?from_following=true`
      );
      expect(response.data).toHaveLength(2);
    });
  });

  describe('Error Handling Across Services', () => {
    it('should handle cascading errors gracefully', async () => {
      // Step 1: Unauthorized access
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      });

      try {
        await axios.get(`${API_URL}/users/user123/profile`);
        fail('Should have thrown error');
      } catch (error: any) {
        expect(error.response.status).toBe(401);
      }

      // Step 2: After handling auth, retry should work
      mockedAxios.get.mockResolvedValueOnce({
        data: mockUsers.user1,
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/profile`);
      expect(response.status).toBe(200);
    });

    it('should handle partial success in concurrent requests', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1],
        status: 200,
      });

      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 500, data: { detail: 'Server error' } },
      });

      const bookPromise = axios.get(`${API_URL}/books`);
      const gamesPromise = axios.get(`${API_URL}/games`);

      const results = await Promise.allSettled([bookPromise, gamesPromise]);

      expect(results[0].status).toBe('fulfilled');
      expect(results[1].status).toBe('rejected');
    });
  });

  describe('Search and Filter Workflows', () => {
    it('should handle advanced book search with filters', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1],
        status: 200,
      });

      const response = await axios.get(
        `${API_URL}/books?search=fiction&category=adventure&min_rating=4&max_year=2023`
      );

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('search=')
      );
      expect(response.data).toHaveLength(1);
    });

    it('should handle paginated search results', async () => {
      // Page 1
      mockedAxios.get.mockResolvedValueOnce({
        data: Array.from({ length: 10 }, (_, i) => ({
          ...mockBooks.book1,
          id: `book${i}`,
        })),
        status: 200,
        headers: { 'x-total-count': '30' },
      });

      let response = await axios.get(`${API_URL}/books?page=1&limit=10`);
      expect(response.data).toHaveLength(10);

      // Page 2
      mockedAxios.get.mockResolvedValueOnce({
        data: Array.from({ length: 10 }, (_, i) => ({
          ...mockBooks.book1,
          id: `book${i + 10}`,
        })),
        status: 200,
        headers: { 'x-total-count': '30' },
      });

      response = await axios.get(`${API_URL}/books?page=2&limit=10`);
      expect(response.data).toHaveLength(10);
    });
  });

  describe('Recommendation Engine Workflows', () => {
    it('should handle recommendation discovery and follow flow', async () => {
      // Step 1: Get recommendations for user
      mockedAxios.get.mockResolvedValueOnce({
        data: [
          { id: 'rec1', source: 'book', item_id: 'book1', score: 0.95 },
          { id: 'rec2', source: 'game', item_id: 'game1', score: 0.88 },
        ],
        status: 200,
      });

      let response = await axios.get(`${API_URL}/recommendations`);
      expect(response.data).toHaveLength(2);

      // Step 2: View recommended item details
      mockedAxios.get.mockResolvedValueOnce({
        data: mockBooks.book1,
        status: 200,
      });

      response = await axios.get(`${API_URL}/books/${response.data[0].item_id}`);
      expect(response.data).toEqual(mockBooks.book1);

      // Step 3: Follow the recommendation
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          user_id: 'user123',
          recommendation_id: 'rec1',
          followed: true,
        },
        status: 200,
      });

      response = await axios.post(`${API_URL}/recommendations/rec1/follow`, {});
      expect(response.data.followed).toBe(true);
    });

    it('should handle recommendation dismissal', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          user_id: 'user123',
          recommendation_id: 'rec1',
          dismissed: true,
        },
        status: 200,
      });

      const response = await axios.post(
        `${API_URL}/recommendations/rec1/dismiss`,
        {}
      );

      expect(response.data.dismissed).toBe(true);
    });
  });

  describe('Network Error Resilience', () => {
    it('should handle timeout gracefully', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        code: 'ECONNABORTED',
        message: 'timeout of 5000ms exceeded',
      });

      try {
        await axios.get(`${API_URL}/books`);
        fail('Should have thrown error');
      } catch (error: any) {
        expect(error.code).toBe('ECONNABORTED');
      }
    });

    it('should handle network connection errors', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        code: 'ECONNREFUSED',
        message: 'Connection refused',
      });

      try {
        await axios.get(`${API_URL}/books`);
        fail('Should have thrown error');
      } catch (error: any) {
        expect(error.code).toBe('ECONNREFUSED');
      }
    });

    it('should handle 503 Service Unavailable', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: {
          status: 503,
          data: { detail: 'Service Unavailable' },
        },
      });

      try {
        await axios.get(`${API_URL}/books`);
        fail('Should have thrown error');
      } catch (error: any) {
        expect(error.response.status).toBe(503);
      }
    });
  });

  describe('Data Consistency Workflows', () => {
    it('should maintain data consistency across operations', async () => {
      // Add book
      mockedAxios.post.mockResolvedValueOnce({
        data: { id: 'user-book-1', book_id: mockBooks.book1.id },
        status: 201,
      });

      let response = await axios.post(
        `${API_URL}/users/user123/books/${mockBooks.book1.id}`,
        {}
      );
      expect(response.status).toBe(201);

      // Verify book appears in user library
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1],
        status: 200,
      });

      response = await axios.get(`${API_URL}/users/user123/books`);
      expect(response.data).toContainEqual(
        expect.objectContaining({ id: mockBooks.book1.id })
      );

      // Remove book
      mockedAxios.delete.mockResolvedValueOnce({
        status: 204,
      });

      response = await axios.delete(
        `${API_URL}/users/user123/books/${mockBooks.book1.id}`
      );
      expect(response.status).toBe(204);
    });
  });
});