import {create} from 'zustand';
import type {User} from '../types/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setAuthenticated: (isAuthenticated: boolean) => void;
  setLoading: (isLoading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>(set => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  setUser: (user: User | null) => set({user}),
  setAuthenticated: (isAuthenticated: boolean) => set({isAuthenticated}),
  setLoading: (isLoading: boolean) => set({isLoading}),
  logout: () => set({user: null, isAuthenticated: false}),
}));
