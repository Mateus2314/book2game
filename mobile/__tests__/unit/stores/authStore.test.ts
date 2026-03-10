import { renderHook, act } from '@testing-library/react-native';
import { useAuthStore } from '@/stores/authStore';
import { mockUsers } from '../../helpers/mockData';
import type { User } from '@/types/api';

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset store to initial state before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: true,
    });
  });

  it('should have initial state', () => {
    const { result } = renderHook(() => useAuthStore());

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(true);
  });

  it('should set user', () => {
    const { result } = renderHook(() => useAuthStore());
    const user = mockUsers.user1 as User;

    act(() => {
      result.current.setUser(user);
    });

    expect(result.current.user).toEqual(user);
  });

  it('should clear user when setUser(null)', () => {
    const { result } = renderHook(() => useAuthStore());
    const user = mockUsers.user1 as User;

    act(() => {
      result.current.setUser(user);
    });

    expect(result.current.user).toEqual(user);

    act(() => {
      result.current.setUser(null);
    });

    expect(result.current.user).toBeNull();
  });

  it('should set authenticated state', () => {
    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.setAuthenticated(true);
    });

    expect(result.current.isAuthenticated).toBe(true);

    act(() => {
      result.current.setAuthenticated(false);
    });

    expect(result.current.isAuthenticated).toBe(false);
  });

  it('should set loading state', () => {
    const { result } = renderHook(() => useAuthStore());

    expect(result.current.isLoading).toBe(true);

    act(() => {
      result.current.setLoading(false);
    });

    expect(result.current.isLoading).toBe(false);

    act(() => {
      result.current.setLoading(true);
    });

    expect(result.current.isLoading).toBe(true);
  });

  it('should logout and clear state', () => {
    const { result } = renderHook(() => useAuthStore());
    const user = mockUsers.user1 as User;

    act(() => {
      result.current.setUser(user);
      result.current.setAuthenticated(true);
    });

    expect(result.current.user).toEqual(user);
    expect(result.current.isAuthenticated).toBe(true);

    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('should handle multiple state changes', () => {
    const { result } = renderHook(() => useAuthStore());
    const user1 = mockUsers.user1 as User;
    const user2 = mockUsers.user2 as User;

    act(() => {
      result.current.setUser(user1);
      result.current.setAuthenticated(true);
      result.current.setLoading(false);
    });

    expect(result.current.user).toEqual(user1);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.isLoading).toBe(false);

    act(() => {
      result.current.setUser(user2);
    });

    expect(result.current.user).toEqual(user2);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.isLoading).toBe(false);
  });

  it('should be independent across hook instances', () => {
    const { result: result1 } = renderHook(() => useAuthStore());
    const { result: result2 } = renderHook(() => useAuthStore());
    const user = mockUsers.user1 as User;

    act(() => {
      result1.current.setUser(user);
      result1.current.setAuthenticated(true);
    });

    // Both instances share the same store
    expect(result2.current.user).toEqual(user);
    expect(result2.current.isAuthenticated).toBe(true);
  });

  it('should handle rapid state updates', () => {
    const { result } = renderHook(() => useAuthStore());

    act(() => {
      result.current.setLoading(true);
      result.current.setLoading(false);
      result.current.setLoading(true);
      result.current.setLoading(false);
    });

    expect(result.current.isLoading).toBe(false);
  });
});