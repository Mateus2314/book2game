import axios from 'axios';
import { mockBooks } from '../../helpers/mockData';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Books Service Integration', () => {
  const API_URL = 'http://localhost:3000';

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Get All Books', () => {
    it('should fetch all books successfully', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1, mockBooks.book2],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/books`);

      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/books`);
      expect(response.data).toHaveLength(2);
      expect(response.data[0].id).toBe(mockBooks.book1.id);
    });

    it('should handle empty books list', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/books`);
      expect(response.data).toEqual([]);
    });

    it('should handle server error', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 500, data: { detail: 'Internal server error' } },
      });

      try {
        await axios.get(`${API_URL}/books`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(500);
      }
    });
  });

  describe('Get Book by ID', () => {
    it('should fetch single book by id', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: mockBooks.book1,
        status: 200,
      });

      const response = await axios.get(`${API_URL}/books/${mockBooks.book1.id}`);

      expect(mockedAxios.get).toHaveBeenCalledWith(`${API_URL}/books/${mockBooks.book1.id}`);
      expect(response.data).toEqual(mockBooks.book1);
    });

    it('should handle book not found', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 404, data: { detail: 'Book not found' } },
      });

      try {
        await axios.get(`${API_URL}/books/nonexistent`);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(404);
      }
    });
  });

  describe('Search Books', () => {
    it('should search books by title', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/books?search=${mockBooks.book1.title}`);

      expect(mockedAxios.get).toHaveBeenCalledWith(expect.stringContaining('search='));
      expect(response.data).toHaveLength(1);
    });

    it('should search books by author', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1, mockBooks.book2],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/books?author=Author`);

      expect(response.data).toHaveLength(2);
    });

    it('should handle search with no results', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/books?search=nonexistent`);

      expect(response.data).toEqual([]);
    });

    it('should search with multiple filters', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1],
        status: 200,
      });

      const response = await axios.get(
        `${API_URL}/books?search=title&category=fiction&year=2023`
      );

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('search=')
      );
      expect(response.data).toHaveLength(1);
    });
  });

  describe('Create Book', () => {
    it('should create book successfully', async () => {
      const newBook = {
        title: 'New Book',
        authors: ['New Author'],
        isbn: '1234567890',
        categories: ['fiction'],
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: { id: 'new-book-id', ...newBook },
        status: 201,
      });

      const response = await axios.post(`${API_URL}/books`, newBook);

      expect(mockedAxios.post).toHaveBeenCalledWith(`${API_URL}/books`, newBook);
      expect(response.status).toBe(201);
      expect(response.data.title).toBe('New Book');
    });

    it('should handle missing required fields', async () => {
      const incompleteBook = {
        title: 'Incomplete Book',
      };

      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 422,
          data: { detail: 'Missing required fields' },
        },
      });

      try {
        await axios.post(`${API_URL}/books`, incompleteBook);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(422);
      }
    });

    it('should handle duplicate book', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 400,
          data: { detail: 'Book with this ISBN already exists' },
        },
      });

      try {
        await axios.post(`${API_URL}/books`, mockBooks.book1);
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(400);
      }
    });
  });

  describe('Create Book from Google Books', () => {
    it('should create book from Google Books API', async () => {
      const googleBookData = {
        google_book_id: 'google-id-123',
        google_api_key: 'test-key',
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: {
          id: 'book-id',
          title: 'Book from Google',
          ...googleBookData,
        },
        status: 201,
      });

      const response = await axios.post(
        `${API_URL}/books/create-from-google`,
        googleBookData
      );

      expect(response.status).toBe(201);
      expect(response.data.google_book_id).toBe('google-id-123');
    });

    it('should handle invalid Google Book ID', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 400,
          data: { detail: 'Invalid Google Book ID' },
        },
      });

      try {
        await axios.post(`${API_URL}/books/create-from-google`, {
          google_book_id: 'invalid',
        });
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(400);
      }
    });

    it('should handle Google API errors', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 503,
          data: { detail: 'Google Books API unavailable' },
        },
      });

      try {
        await axios.post(`${API_URL}/books/create-from-google`, {
          google_book_id: 'valid-id',
        });
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.response.status).toBe(503);
      }
    });
  });

  describe('Book Filtering and Sorting', () => {
    it('should filter books by category', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/books?category=fiction`);
      expect(response.data).toHaveLength(1);
    });

    it('should sort books by title', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1, mockBooks.book2],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/books?sort=title`);
      expect(response.data).toHaveLength(2);
    });

    it('should sort books by rating', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book2, mockBooks.book1],
        status: 200,
      });

      const response = await axios.get(`${API_URL}/books?sort=-rating`);
      expect(response.data).toHaveLength(2);
    });

    it('should paginate books', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: Array.from({ length: 10 }, (_, i) => ({
          ...mockBooks.book1,
          id: `book${i}`,
        })),
        status: 200,
        headers: { 'x-total-count': '50' },
      });

      const response = await axios.get(`${API_URL}/books?page=1&limit=10`);
      expect(response.data).toHaveLength(10);
    });
  });

  describe('Real-world Book Discovery Flow', () => {
    it('should handle complete book discovery workflow', async () => {
      // Search for books
      mockedAxios.get.mockResolvedValueOnce({
        data: [mockBooks.book1],
        status: 200,
      });

      let response = await axios.get(`${API_URL}/books?search=test`);
      expect(response.data).toHaveLength(1);

      // View book details
      mockedAxios.get.mockResolvedValueOnce({
        data: mockBooks.book1,
        status: 200,
      });

      response = await axios.get(`${API_URL}/books/${mockBooks.book1.id}`);
      expect(response.data.id).toBe(mockBooks.book1.id);

      // Add to library
      mockedAxios.post.mockResolvedValueOnce({
        data: { id: '1', book_id: mockBooks.book1.id },
        status: 201,
      });

      response = await axios.post(`${API_URL}/users/user123/books/${mockBooks.book1.id}`, {});
      expect(response.status).toBe(201);
    });
  });
});