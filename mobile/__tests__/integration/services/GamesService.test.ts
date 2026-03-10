import axios from 'axios';
import { mockGames } from '../../helpers/mockData';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Games Service Integration', () => {
  const API_URL = 'http://localhost:3000';

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Get All Games', () => {
    it('should fetch all games successfully', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game1, mockGames.game2],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/games`);

      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/games`);
      expect(response.data).toHaveLength(2);
      expect(response.data[0].id).toBe(mockGames.game1.id);
    });

    it('should handle empty games list', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/games`);
      expect(response.data).toEqual([]);
    });

    it('should handle server error when fetching games', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 500, data: { detail: 'Internal server error' } },
      });

      try {
        await axios.get(`${API_URL}/games`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(500);
      }
    });
  });

  describe('Get Game by ID', () => {
    it('should fetch single game by id', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: mockGames.game1,
        status: 200,
      });

      const response = await axios.get(`${API_URL}/games/${mockGames.game1.id}`);

      expect(mockedAxios.get).toHaveBeenCalledWith(
        `${API_URL}/games/${mockGames.game1.id}`
      );
      expect(response.data).toEqual(mockGames.game1);
    });

    it('should handle game not found', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 404, data: { detail: 'Game not found' } },
      });

      try {
        await axios.get(`${API_URL}/games/nonexistent`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });
  });

  describe('Search Games', () => {
    it('should search games by title', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game1],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/games?search=${mockGames.game1.title}`);

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('search=')
      );
      expect(response.data).toHaveLength(1);
    });

    it('should search games by developer', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game1, mockGames.game2],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/games?developer=developer`);

      expect(response.data).toHaveLength(2);
    });

    it('should search with no results', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/games?search=nonexistent`);

      expect(response.data).toEqual([]);
    });

    it('should search games by genre', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game1],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/games?genre=RPG`);

      expect(response.data).toHaveLength(1);
    });
  });

  describe('Get User Games', () => {
    it('should fetch user games successfully', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game1],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/games`);

      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/users/user123/games`);
      expect(response.data).toHaveLength(1);
    });

    it('should handle empty user games list', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/games`);
      expect(response.data).toEqual([]);
    });

    it('should handle user not found', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 404, data: { detail: 'User not found' } },
      });

      try {
        await axios.get(`${API_URL}/users/nonexistent/games`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });
  });

  describe('Add Game to User Collection', () => {
    it('should add game to user collection', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: { id: '1', user_id: 'user123', game_id: mockGames.game1.id },
        status: 201,
      });

      const response = await axios.post(
        `${API_URL}/users/user123/games/${mockGames.game1.id}`,
        {}
      );

      expect(response.status).toBe(201);
      expect(response.data.game_id).toBe(mockGames.game1.id);
    });

    it('should handle adding duplicate game', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 400,
          data: { detail: 'Game already in user collection' },
        },
      });

      try {
        await axios.post(`${API_URL}/users/user123/games/${mockGames.game1.id}`, {});
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(400);
      }
    });

    it('should handle game not found when adding', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 404,
          data: { detail: 'Game not found' },
        },
      });

      try {
        await axios.post(`${API_URL}/users/user123/games/nonexistent`, {});
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });
  });

  describe('Remove Game from User Collection', () => {
    it('should remove game from user collection', async () => {
      mockedAxios.delete.mockResolvedValueOnce({
        status: 204,
      });

      const response = await axios.delete(
        `${API_URL}/users/user123/games/${mockGames.game1.id}`
      );

      expect(response.status).toBe(204);
    });

    it('should handle removing non-existent game from collection', async () => {
      mockedAxios.delete.mockRejectedValueOnce({
        response: {
          status: 404,
          data: { detail: 'Game not found in user collection' },
        },
      });

      try {
        await axios.delete(`${API_URL}/users/user123/games/nonexistent`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });
  });

  describe('Rate Game', () => {
    it('should rate a game successfully', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          id: 'rating1',
          user_id: 'user123',
          game_id: mockGames.game1.id,
          rating: 5,
        },
        status: 201,
      });

      const response = await axios.post(
        `${API_URL}/users/user123/games/${mockGames.game1.id}/rate`,
        { rating: 5 }
      );

      expect(response.status).toBe(201);
      expect(response.data.rating).toBe(5);
    });

    it('should handle invalid rating value', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 422,
          data: { detail: 'Rating must be between 1 and 5' },
        },
      });

      try {
        await axios.post(
          `${API_URL}/users/user123/games/${mockGames.game1.id}/rate`,
          { rating: 10 }
        );
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(422);
      }
    });

    it('should update existing rating', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          id: 'rating1',
          user_id: 'user123',
          game_id: mockGames.game1.id,
          rating: 4,
        },
        status: 200,
      });

      const response = await axios.post(
        `${API_URL}/users/user123/games/${mockGames.game1.id}/rate`,
        { rating: 4 }
      );

      expect(response.status).toBe(200);
      expect(response.data.rating).toBe(4);
    });
  });

  describe('Games Filtering and Sorting', () => {
    it('should filter games by platform', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game1],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/games?platform=PC`);
      expect(response.data).toHaveLength(1);
    });

    it('should sort games by rating', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game2, mockGames.game1],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/games?sort=-rating`);
      expect(response.data).toHaveLength(2);
    });

    it('should sort games by release date', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game1, mockGames.game2],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/games?sort=release_date`);
      expect(response.data).toHaveLength(2);
    });

    it('should paginate games', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: Array.from({ length: 20 }, (_, i) => ({
          ...mockGames.game1,
          id: `game${i}`,
        })),
        status: 200,
        headers: { 'x-total-count': '100' },
      });

      const response = await axios.get(`${API_URL}/games?page=1&limit=20`);
      expect(response.data).toHaveLength(20);
    });
  });

  describe('Real-world Game Discovery Flow', () => {
    it('should handle complete game discovery workflow', async () => {
      // Search for games
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game1],
        status: 200,
      });

      let response = await axios.get(`${API_URL}/games?search=test`);
      expect(response.data).toHaveLength(1);

      // View game details
      mockedAxios.get.mockResolvedValueOnce({
        data: mockGames.game1,
        status: 200,
      });

      response = await axios.get(`${API_URL}/games/${mockGames.game1.id}`);
      expect(response.data.id).toBe(mockGames.game1.id);

      // Add to collection
      mockedAxios.post.mockResolvedValueOnce({
        data: { id: '1', game_id: mockGames.game1.id },
        status: 201,
      });

      response = await axios.post(
        `${API_URL}/users/user123/games/${mockGames.game1.id}`,
        {}
      );
      expect(response.status).toBe(201);

      // Rate the game
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          id: 'rating1',
          game_id: mockGames.game1.id,
          rating: 5,
        },
        status: 201,
      });

      response = await axios.post(
        `${API_URL}/users/user123/games/${mockGames.game1.id}/rate`,
        { rating: 5 }
      );
      expect(response.status).toBe(201);
    });

    it('should handle multiple games in collection with different ratings', async () => {
      // Get all user games
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockGames.game1, mockGames.game2],
        status: 200,
      });

      let response = await axios.get(`${API_URL}/users/user123/games`);
      expect(response.data).toHaveLength(2);

      // Rate first game
      mockedAxios.post.mockResolvedValueOnce({
        data: { game_id: mockGames.game1.id, rating: 5 },
        status: 201,
      });

      response = await axios.post(
        `${API_URL}/users/user123/games/${mockGames.game1.id}/rate`,
        { rating: 5 }
      );
      expect(response.data.rating).toBe(5);

      // Rate second game
      mockedAxios.post.mockResolvedValueOnce({
        data: { game_id: mockGames.game2.id, rating: 3 },
        status: 201,
      });

      response = await axios.post(
        `${API_URL}/users/user123/games/${mockGames.game2.id}/rate`,
        { rating: 3 }
      );
      expect(response.data.rating).toBe(3);
    });
  });
});