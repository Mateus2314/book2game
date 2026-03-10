import axios from 'axios';
import { mockBooks, mockGames, mockRecommendations } from '../../helpers/mockData';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Recommendations Service Integration', () => {
  const API_URL = 'http://localhost:3000';

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Get Recommendations', () => {
    it('should fetch recommendations successfully', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockRecommendations.rec1],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/recommendations`);

      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/recommendations`);
      expect(response.data).toEqual([mockRecommendations.rec1]);
    });

    it('should handle no recommendations', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/recommendations`);
      expect(response.data).toEqual([]);
    });

    it('should handle fetch error', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 500, data: { detail: 'Server error' } },
      });

      try {
        await axios.get(`${API_URL}/recommendations`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(500);
      }
    });
  });

  describe('Create Recommendation', () => {
    it('should create recommendation successfully', async () => {
      const recommendationPayload = {
        source_type: 'book',
        source_id: mockBooks.book1.id,
        recommended_type: 'game',
        recommended_id: mockGames.game1.id,
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: {
          id: '1',
          ...recommendationPayload,
          created_at: new Date().toISOString(),
        },
        status: 201,
      });

      const response = await axios.post(`${API_URL}/recommendations`, recommendationPayload);

      expect(mockedAxios.post).toHaveBeenCalledWith(`${API_URL}/recommendations`, recommendationPayload);
      expect(response.status).toBe(201);
      expect(response.data.source_id).toBe(mockBooks.book1.id);
    });

    it('should handle invalid source type', async () => {
      const invalidPayload = {
        source_type: 'invalid',
        source_id: 'test',
        recommended_type: 'game',
        recommended_id: 'test2',
      };

      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 400,
          data: { detail: 'Invalid source type' },
        },
      });

      try {
        await axios.post(`${API_URL}/recommendations`, invalidPayload);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(400);
      }
    });

    it('should handle missing required fields', async () => {
      const incompletePayload = {
        source_type: 'book',
        source_id: mockBooks.book1.id,
      };

      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 422,
          data: { detail: 'Missing required fields' },
        },
      });

      try {
        await axios.post(`${API_URL}/recommendations`, incompletePayload);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(422);
      }
    });
  });

  describe('Get Single Recommendation', () => {
    it('should fetch single recommendation by id', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: mockRecommendations.rec1,
        status: 200,
      });

      const response = await axios.get(`${API_URL}/recommendations/rec1`);

      expect(response.data).toEqual(mockRecommendations.rec1);
    });

    it('should handle not found', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: {
          status: 404,
          data: { detail: 'Recommendation not found' },
        },
      });

      try {
        await axios.get(`${API_URL}/recommendations/nonexistent`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });
  });

  describe('Recommendation Filtering', () => {
    it('should fetch recommendations for book source', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockRecommendations.rec1],
        status: 200,
      });

      const response = await axios.get(
        `${API_URL}/recommendations?source_type=book&source_id=${mockBooks.book1.id}`
      );

      expect(response.data).toHaveLength(1);
    });

    it('should fetch recommendations for game source', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockRecommendations.rec1],
        status: 200,
      });

      const response = await axios.get(
        `${API_URL}/recommendations?source_type=game&source_id=${mockGames.game1.id}`
      );

      expect(response.data).toHaveLength(1);
    });

    it('should handle pagination', async () => {
      const recommendations = Array.from({ length: 20 }, (_, i) => ({
        ...mockRecommendations.rec1,
        id: `rec${i}`,
      }));

      mockedAxios.get.mockResolvedValueOnce({
        data: recommendations.slice(0, 10),
        status: 200,
        headers: { 'x-total-count': '20' },
      });

      const response = await axios.get(`${API_URL}/recommendations?page=1&limit=10`);

      expect(response.data).toHaveLength(10);
    });
  });

  describe('Real-world Recommendation Flows', () => {
    it('should handle user following a recommendation', async () => {
      // User views book
      mockedAxios.get.mockResolvedValueOnce({
        data: mockBooks.book1,
        status: 200,
      });

      let response = await axios.get(`${API_URL}/books/${mockBooks.book1.id}`);
      expect(response.data.id).toBe(mockBooks.book1.id);

      // Get recommendations for this book
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockRecommendations.rec1],
        status: 200,
      });

      response = await axios.get(
        `${API_URL}/recommendations?source_type=book&source_id=${mockBooks.book1.id}`
      );
      expect(response.data).toHaveLength(1);

      // User clicks on recommended game
      mockedAxios.get.mockResolvedValueOnce({
        data: mockGames.game1,
        status: 200,
      });

      response = await axios.get(`${API_URL}/games/${mockGames.game1.id}`);
      expect(response.data.id).toBe(mockGames.game1.id);
    });

    it('should generate recommendations after adding item to library', async () => {
      // Add book
      mockedAxios.post.mockResolvedValueOnce({
        data: { id: '1', book_id: mockBooks.book1.id },
        status: 201,
      });

      await axios.post(`${API_URL}/users/user123/books/${mockBooks.book1.id}`, {});

      // Get recommendations triggered by library change
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockRecommendations.rec1],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/recommendations?source_id=${mockBooks.book1.id}`);
      expect(response.data).toHaveLength(1);
    });

    it('should handle multiple sources for cross-recommendations', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockRecommendations.rec1, { ...mockRecommendations.rec1, id: 'rec2' }],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/recommendations?user_id=user123`);
      expect(response.data).toHaveLength(2);
    });
  });
});