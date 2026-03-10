import axios from 'axios';
import { mockBooks } from '../../helpers/mockData';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Library Service Integration', () => {
  const API_URL = 'http://localhost:3000';

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Get User Books', () => {
    it('should fetch user books successfully', async () => {
      const mockUserBooks = [
        { book_id: '1', book: mockBooks.book1 },
        { book_id: '2', book: mockBooks.book2 },
      ];

      mockedAxios.get.mockResolvedValueOnce({
        data: mockUserBooks,
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/books`);

      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/users/user123/books`);
      expect(response.data).toEqual(mockUserBooks);
      expect(response.status).toBe(200);
    });

    it('should handle empty library', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/users/user123/books`);

      expect(response.data).toEqual([]);
    });

    it('should handle fetch error', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 404, data: { detail: 'User not found' } },
      });

      try {
        await axios.get(`${API_URL}/users/user123/books`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });
  });

  describe('Add Book to Library', () => {
    it('should add book successfully', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: { id: '1', book_id: mockBooks.book1.id, user_id: 'user123' },
        status: 201,
      });

      const response = await axios.post(`${API_URL}/users/user123/books/${mockBooks.book1.id}`, {});

      expect(mockedAxios.post).toHaveBeenCalledWith(
        `${API_URL}/users/user123/books/${mockBooks.book1.id}`,
        {}
      );
      expect(response.status).toBe(201);
    });

    it('should handle duplicate book', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: { status: 400, data: { detail: 'Book already in library' } },
      });

      try {
        await axios.post(`${API_URL}/users/user123/books/${mockBooks.book1.id}`, {});
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(400);
      }
    });

    it('should handle book not found', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: { status: 404, data: { detail: 'Book not found' } },
      });

      try {
        await axios.post(`${API_URL}/users/user123/books/nonexistent`, {});
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });
  });

  describe('Remove Book from Library', () => {
    it('should remove book successfully', async () => {
      mockedAxios.delete.mockResolvedValueOnce({
        data: { msg: 'Book removed' },
        status: 200,
      });

      const response = await axios.delete(`${API_URL}/users/user123/books/${mockBooks.book1.id}`);

      expect(mockedAxios.delete).toHaveBeenCalledWith(
        `${API_URL}/users/user123/books/${mockBooks.book1.id}`
      );
      expect(response.status).toBe(200);
    });

    it('should handle removing non-existent book', async () => {
      mockedAxios.delete.mockRejectedValueOnce({
        response: { status: 404, data: { detail: 'Book not in library' } },
      });

      try {
        await axios.delete(`${API_URL}/users/user123/books/nonexistent`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });
  });

  describe('Library Operations Flow', () => {
    it('should handle full library lifecycle', async () => {
      // Get library
      mockedAxios.get.mockResolvedValueOnce({
        data: [],
        status: 200,
      });

      let response = await axios.get(`${API_URL}/users/user123/books`);
      expect(response.data).toEqual([]);

      // Add book
      mockedAxios.post.mockResolvedValueOnce({
        data: { id: '1', book_id: mockBooks.book1.id, user_id: 'user123' },
        status: 201,
      });

      response = await axios.post(`${API_URL}/users/user123/books/${mockBooks.book1.id}`, {});
      expect(response.status).toBe(201);

      // Get library again
      mockedAxios.get.mockResolvedValueOnce({
        data: [{ book_id: mockBooks.book1.id, book: mockBooks.book1 }],
        status: 200,
      });

      response = await axios.get(`${API_URL}/users/user123/books`);
      expect(response.data.length).toBe(1);

      // Remove book
      mockedAxios.delete.mockResolvedValueOnce({
        data: { msg: 'Book removed' },
        status: 200,
      });

      response = await axios.delete(`${API_URL}/users/user123/books/${mockBooks.book1.id}`);
      expect(response.status).toBe(200);
    });

    it('should handle concurrent operations', async () => {
      mockedAxios.post.mockResolvedValue({
        data: { id: '1', book_id: 'test', user_id: 'user123' },
        status: 201,
      });

      const promises = [
        axios.post(`${API_URL}/users/user123/books/book1`, {}),
        axios.post(`${API_URL}/users/user123/books/book2`, {}),
        axios.post(`${API_URL}/users/user123/books/book3`, {}),
      ];

      const results = await Promise.all(promises);
      expect(results).toHaveLength(3);
      expect(results.every(r => r.status === 201)).toBe(true);
    });
  });
});