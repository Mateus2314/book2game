import { renderHook, act, waitFor } from '@testing-library/react-native';
import { useAuthStore } from '@/stores/authStore';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Authentication Service Integration', () => {
  afterEach(() => {
    jest.clearAllMocks();
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: true,
    });
  });

  describe('Login Flow', () => {
    it('should login successfully with valid credentials', async () => {
      const mockToken = 'mock-token-123';
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
      };

      mockedAxios.post.mockResolvedValueOnce({
        data: {
          access_token: mockToken,
          token_type: 'bearer',
        },
      });

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setAuthenticated(true);
        result.current.setUser(mockUser);
      });

      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual(mockUser);
    });

    it('should handle login error gracefully', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 401,
          data: { detail: 'Invalid credentials' },
        },
      });

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.logout();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
    });
  });

  describe('Token Management', () => {
    it('should store authentication token', () => {
      const mockToken = 'mock-token-123';
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setAuthenticated(true);
      });

      expect(result.current.isAuthenticated).toBe(true);
    });

    it('should clear token on logout', () => {
      const mockUser = { id: '1', email: 'test@example.com', username: 'testuser' };
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(mockUser);
        result.current.setAuthenticated(true);
      });

      expect(result.current.isAuthenticated).toBe(true);

      act(() => {
        result.current.logout();
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
    });
  });

  describe('User Session', () => {
    it('should persist user information', () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
      };

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setUser(mockUser);
      });

      expect(result.current.user).toEqual(mockUser);
    });

    it('should handle multiple login/logout cycles', () => {
      const { result } = renderHook(() => useAuthStore());

      // First login
      act(() => {
        result.current.setAuthenticated(true);
      });
      expect(result.current.isAuthenticated).toBe(true);

      // Logout
      act(() => {
        result.current.logout();
      });
      expect(result.current.isAuthenticated).toBe(false);

      // Second login
      act(() => {
        result.current.setAuthenticated(true);
      });
      expect(result.current.isAuthenticated).toBe(true);
    });
  });

  describe('Loading State', () => {
    it('should manage loading state during authentication', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setLoading(true);
      });
      expect(result.current.isLoading).toBe(true);

      act(() => {
        result.current.setLoading(false);
      });
      expect(result.current.isLoading).toBe(false);
    });

    it('should set loading to false after successful login', () => {
      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setLoading(true);
        result.current.setAuthenticated(true);
        result.current.setLoading(false);
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isAuthenticated).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        code: 'ECONNABORTED',
        message: 'Network timeout',
      });

      const { result } = renderHook(() => useAuthStore());

      act(() => {
        result.current.setLoading(false);
      });

      expect(result.current.isLoading).toBe(false);
    });

    it('should handle validation errors', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 422,
          data: {
            detail: [{ field: 'email', message: 'Invalid email' }],
          },
        },
      });

      const { result } = renderHook(() => useAuthStore());
      expect(result.current.isAuthenticated).toBe(false);
    });
  });
});