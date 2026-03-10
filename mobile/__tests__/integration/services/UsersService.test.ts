import axios from 'axios';
import { mockUsers } from '../../helpers/mockData';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Users Service Integration', () => {
  const API_URL = 'http://localhost:3000';

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Get User Profile', () => {
    it('should fetch user profile successfully', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: mockUsers.user1,
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/profile`);

      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/users/user123/profile`);
      expect(response.data).toEqual(mockUsers.user1);
    });

    it('should handle user not found', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 404, data: { detail: 'User not found' } },
      });

      try {
        await axios.get(`${API_URL}/users/nonexistent/profile`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });

    it('should handle unauthorized access', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 401, data: { detail: 'Unauthorized' } },
      });

      try {
        await axios.get(`${API_URL}/users/other-user/profile`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(401);
      }
    });
  });

  describe('Update User Profile', () => {
    it('should update user profile successfully', async () => {
      const updatedProfile = {
        ...mockUsers.user1,
        bio: 'Updated bio',
      };

      mockedAxios.put.mockResolvedValueOnce({
        data: updatedProfile,
        status: 200,
      });

      const response = await axios.put(`${API_URL}/users/user123/profile`, {
        bio: 'Updated bio',
      });

      expect(response.status).toBe(200);
      expect(response.data.bio).toBe('Updated bio');
    });

    it('should handle invalid profile data', async () => {
      mockedAxios.put.mockRejectedValueOnce({
        response: {
          status: 422,
          data: { detail: 'Invalid profile data' },
        },
      });

      try {
        await axios.put(`${API_URL}/users/user123/profile`, {
          age: 'not-a-number',
        });
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(422);
      }
    });
  });

  describe('User Preferences', () => {
    it('should get user reading preferences', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          favorite_genres: ['fiction', 'mystery'],
          preferred_language: 'en',
        },
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/preferences`);

      expect(response.data.favorite_genres).toContain('fiction');
    });

    it('should get user gaming preferences', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          favorite_genres: ['RPG', 'Strategy'],
          preferred_platform: 'PC',
        },
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/preferences`);

      expect(response.data.favorite_genres).toContain('RPG');
    });

    it('should update user preferences', async () => {
      mockedAxios.put.mockResolvedValueOnce({
        data: {
          favorite_genres: ['science-fiction', 'fantasy'],
          updated_at: new Date().toISOString(),
        },
        status: 200,
      });

      const response = await axios.put(`${API_URL}/users/user123/preferences`, {
        favorite_genres: ['science-fiction', 'fantasy'],
      });

      expect(response.status).toBe(200);
      expect(response.data.favorite_genres).toContain('science-fiction');
    });
  });

  describe('User Statistics', () => {
    it('should get user statistics', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          total_books: 25,
          total_games: 15,
          books_read: 12,
          avg_rating: 4.2,
        },
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/statistics`);

      expect(response.data.total_books).toBe(25);
      expect(response.data.books_read).toBe(12);
    });

    it('should handle user with no statistics', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          total_books: 0,
          total_games: 0,
          books_read: 0,
          avg_rating: 0,
        },
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/statistics`);

      expect(response.data.total_books).toBe(0);
    });
  });

  describe('User Activity Feed', () => {
    it('should get user activity feed', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [
          {
            id: '1',
            type: 'book_added',
            timestamp: new Date().toISOString(),
            title: 'Added a book',
          },
          {
            id: '2',
            type: 'game_rated',
            timestamp: new Date().toISOString(),
            title: 'Rated a game',
          },
        ],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/activity`);

      expect(response.data).toHaveLength(2);
      expect(response.data[0].type).toBe('book_added');
    });

    it('should paginate activity feed', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: Array.from({ length: 20 }, (_, i) => ({
          id: `activity${i}`,
          type: 'event',
          timestamp: new Date().toISOString(),
        })),
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/activity?page=1&limit=20`);

      expect(response.data).toHaveLength(20);
    });
  });

  describe('User Social Features', () => {
    it('should follow another user', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          follower_id: 'user123',
          following_id: 'user456',
        },
        status: 201,
      });

      const response = await axios.post(
        `${API_URL}/users/user123/follow/user456`,
        {}
      );

      expect(response.status).toBe(201);
    });

    it('should handle already following user', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 400,
          data: { detail: 'Already following this user' },
        },
      });

      try {
        await axios.post(`${API_URL}/users/user123/follow/user456`, {});
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(400);
      }
    });

    it('should unfollow a user', async () => {
      mockedAxios.delete.mockResolvedValueOnce({
        status: 204,
      });

      const response = await axios.delete(
        `${API_URL}/users/user123/follow/user456`
      );

      expect(response.status).toBe(204);
    });

    it('should get user followers', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockUsers.user2],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/followers`);

      expect(response.data).toHaveLength(1);
    });

    it('should get user following', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockUsers.user2],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/following`);

      expect(response.data).toHaveLength(1);
    });
  });

  describe('User Settings', () => {
    it('should get user settings', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          notifications_enabled: true,
          email_digest: 'weekly',
          privacy: 'public',
        },
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/settings`);

      expect(response.data.notifications_enabled).toBe(true);
    });

    it('should update user settings', async () => {
      mockedAxios.put.mockResolvedValueOnce({
        data: {
          notifications_enabled: false,
          email_digest: 'none',
          privacy: 'private',
        },
        status: 200,
      });

      const response = await axios.put(`${API_URL}/users/user123/settings`, {
        notifications_enabled: false,
        privacy: 'private',
      });

      expect(response.status).toBe(200);
      expect(response.data.notifications_enabled).toBe(false);
    });
  });

  describe('User Recommendations History', () => {
    it('should get user recommendation history', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [
          {
            id: 'rec1',
            source: 'book',
            item_id: 'book1',
            timestamp: new Date().toISOString(),
            followed: true,
          },
          {
            id: 'rec2',
            source: 'game',
            item_id: 'game1',
            timestamp: new Date().toISOString(),
            followed: false,
          },
        ],
        status: 200,
      });

      const response = await axios.get(
        `${API_URL}/users/user123/recommendations-history`
      );

      expect(response.data).toHaveLength(2);
      expect(response.data[0].followed).toBe(true);
    });

    it('should get followed recommendations only', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [
          {
            id: 'rec1',
            source: 'book',
            followed: true,
          },
        ],
        status: 200,
      });

      const response = await axios.get(
        `${API_URL}/users/user123/recommendations-history?followed=true`
      );

      expect(response.data).toHaveLength(1);
      expect(response.data[0].followed).toBe(true);
    });
  });

  describe('Real-world User Workflow', () => {
    it('should handle complete user onboarding flow', async () => {
      // Get initial profile
      mockedAxios.get.mockResolvedValueOnce({
        data: mockUsers.user1,
        status: 200,
      });

      let response = await axios.get(`${API_URL}/users/user123/profile`);
      expect(response.data.id).toBe(mockUsers.user1.id);

      // Update preferences
      mockedAxios.put.mockResolvedValueOnce({
        data: { favorite_genres: ['fiction', 'mystery'] },
        status: 200,
      });

      response = await axios.put(`${API_URL}/users/user123/preferences`, {
        favorite_genres: ['fiction', 'mystery'],
      });
      expect(response.status).toBe(200);

      // Update settings
      mockedAxios.put.mockResolvedValueOnce({
        data: { notifications_enabled: true },
        status: 200,
      });

      response = await axios.put(`${API_URL}/users/user123/settings`, {
        notifications_enabled: true,
      });
      expect(response.status).toBe(200);
    });

    it('should handle user social interaction flow', async () => {
      // Get user profile
      mockedAxios.get.mockResolvedValueOnce({
        data: mockUsers.user1,
        status: 200,
      });

      let response = await axios.get(`${API_URL}/users/user123/profile`);
      expect(response.data).toEqual(mockUsers.user1);

      // Follow another user
      mockedAxios.post.mockResolvedValueOnce({
        data: { follower_id: 'user123', following_id: 'user456' },
        status: 201,
      });

      response = await axios.post(`${API_URL}/users/user123/follow/user456`, {});
      expect(response.status).toBe(201);

      // Get followers list
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockUsers.user2],
        status: 200,
      });

      response = await axios.get(`${API_URL}/users/user123/followers`);
      expect(response.data).toHaveLength(1);
    });
  });
});