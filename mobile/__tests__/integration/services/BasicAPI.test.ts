import axios from 'axios';
import { createMockBook, createMockGame, createMockUser } from '../../helpers/mockData';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Services - Simple Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Book API', () => {
    it('should fetch books list', async () => {
      const mockBooks = [createMockBook(), createMockBook()];
      mockedAxios.get.mockResolvedValue({ data: mockBooks });

      const response = await mockedAxios.get('/books');
      
      expect(response.data).toHaveLength(2);
      expect(response.data[0]).toHaveProperty('id');
      expect(response.data[0]).toHaveProperty('title');
    });

    it('should handle book creation', async () => {
      const newBook = createMockBook();
      mockedAxios.post.mockResolvedValue({ data: newBook, status: 201 });

      const response = await mockedAxios.post('/books', newBook);
      
      expect(response.status).toBe(201);
      expect(response.data.id).toBe(newBook.id);
    });

    it('should handle API errors gracefully', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Network error'));

      try {
        await mockedAxios.get('/books');
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeTruthy();
      }
    });
  });

  describe('Game API', () => {
    it('should fetch games list', async () => {
      const mockGames = [createMockGame(), createMockGame()];
      mockedAxios.get.mockResolvedValue({ data: mockGames });

      const response = await mockedAxios.get('/games');
      
      expect(response.data).toHaveLength(2);
      expect(response.data[0]).toHaveProperty('id');
      expect(response.data[0]).toHaveProperty('name');
    });

    it('should fetch games with pagination', async () => {
      const mockGame = createMockGame();
      mockedAxios.get.mockResolvedValue({ 
        data: [mockGame],
        headers: { 'x-total-count': '100' }
      });

      const response = await mockedAxios.get('/games?skip=0&limit=10');
      
      expect(response.data).toHaveLength(1);
      expect(response.headers['x-total-count']).toBe('100');
    });
  });

  describe('User API', () => {
    it('should fetch user profile', async () => {
      const mockUser = createMockUser();
      mockedAxios.get.mockResolvedValue({ data: mockUser });

      const response = await mockedAxios.get('/users/me');
      
      expect(response.data.id).toBe(mockUser.id);
      expect(response.data.email).toBe(mockUser.email);
    });

    it('should update user profile', async () => {
      const mockUser = createMockUser();
      mockedAxios.put.mockResolvedValue({ data: mockUser });

      const response = await mockedAxios.put('/users/1', { 
        email: 'newemail@example.com' 
      });
      
      expect(response.data.id).toBe(mockUser.id);
    });
  });

  describe('Error Handling', () => {
    it('should handle 404 errors', async () => {
      const error = new Error('Not found');
      (error as any).response = { status: 404 };
      mockedAxios.get.mockRejectedValue(error);

      try {
        await mockedAxios.get('/books/nonexistent');
        fail('Should have thrown');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });

    it('should handle 401 unauthorized', async () => {
      const error = new Error('Unauthorized');
      (error as any).response = { status: 401 };
      mockedAxios.get.mockRejectedValue(error);

      try {
        await mockedAxios.get('/users/me');
        fail('Should have thrown');
      } catch (error: any) {
        expect(error.response.status).toBe(401);
      }
    });

    it('should handle 500 server errors', async () => {
      const error = new Error('Server error');
      (error as any).response = { status: 500 };
      mockedAxios.get.mockRejectedValue(error);

      try {
        await mockedAxios.get('/books');
        fail('Should have thrown');
      } catch (error: any) {
        expect(error.response.status).toBe(500);
      }
    });
  });
});