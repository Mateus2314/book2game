import { renderHook } from '@testing-library/react-native';
import { useErrorHandler } from '@/hooks/useErrorHandler';
import { AxiosError } from 'axios';
import type { ApiError } from '@/types/api';

describe('useErrorHandler', () => {
  it('should return handleError function', () => {
    const { result } = renderHook(() => useErrorHandler());
    expect(result.current.handleError).toBeDefined();
    expect(typeof result.current.handleError).toBe('function');
  });

  describe('AxiosError handling', () => {
    it('should handle rate limiting error (429)', () => {
      const { result } = renderHook(() => useErrorHandler());
      const error = new AxiosError('Too Many Requests', '429');
      error.response = {
        status: 429,
        data: { detail: 'Rate limit exceeded' } as any,
      } as any;

      const message = result.current.handleError(error);
      expect(message).toBe(
        'Limite de requisições atingido. Tente novamente em alguns minutos.'
      );
    });

    it('should handle unauthorized error (401)', () => {
      const { result } = renderHook(() => useErrorHandler());
      const error = new AxiosError('Unauthorized', '401');
      error.response = {
        status: 401,
        data: { detail: 'Invalid token' } as any,
      } as any;

      const message = result.current.handleError(error);
      expect(message).toBe('Sessão expirada. Faça login novamente.');
    });

    it('should handle not found error (404)', () => {
      const { result } = renderHook(() => useErrorHandler());
      const error = new AxiosError('Not Found', '404');
      error.response = {
        status: 404,
        data: { detail: 'Book not found' } as any,
      } as any;

      const message = result.current.handleError(error);
      expect(message).toBe('Recurso não encontrado.');
    });

    it('should handle server error (5xx)', () => {
      const { result } = renderHook(() => useErrorHandler());
      const error = new AxiosError('Internal Server Error', '500');
      error.response = {
        status: 500,
        data: { detail: 'Internal error' } as any,
      } as any;

      const message = result.current.handleError(error);
      expect(message).toBe('Erro no servidor. Tente novamente mais tarde.');
    });

    it('should handle timeout error', () => {
      const { result } = renderHook(() => useErrorHandler());
      const error = new AxiosError('Timeout');
      error.code = 'ECONNABORTED';
      error.response = undefined;

      const message = result.current.handleError(error);
      expect(message).toBe(
        'Tempo de resposta esgotado. Verifique sua conexão.'
      );
    });

    it('should handle network error (no response)', () => {
      const { result } = renderHook(() => useErrorHandler());
      const error = new AxiosError('Network Error');
      error.response = undefined;

      const message = result.current.handleError(error);
      expect(message).toBe('Erro de conexão. Verifique sua internet.');
    });

    it('should handle API error with detail message', () => {
      const { result } = renderHook(() => useErrorHandler());
      const error = new AxiosError('Bad Request', '400');
      error.response = {
        status: 400,
        data: {
          detail: 'Email already exists',
        } as ApiError,
      } as any;

      const message = result.current.handleError(error);
      expect(message).toBe('Email already exists');
    });

    it('should handle FastAPI validation errors (array of objects)', () => {
      const { result } = renderHook(() => useErrorHandler());
      const error = new AxiosError('Validation Error', '422');
      error.response = {
        status: 422,
        data: [
          { msg: 'Field required' },
          { msg: 'Invalid email' },
        ] as ApiError,
      } as any;

      const message = result.current.handleError(error);
      expect(message).toBe('Field required \n Invalid email');
    });

    it('should handle error with msg field', () => {
      const { result } = renderHook(() => useErrorHandler());
      const error = new AxiosError('Bad Request', '400');
      error.response = {
        status: 400,
        data: {
          msg: 'Custom error message',
        } as ApiError,
      } as any;

      const message = result.current.handleError(error);
      expect(message).toBe('Custom error message');
    });
  });

  describe('Error handling', () => {
    it('should handle Error instance', () => {
      const { result } = renderHook(() => useErrorHandler());
      const error = new Error('Custom error message');

      const message = result.current.handleError(error);
      expect(message).toBe('Custom error message');
    });

    it('should handle unknown error type', () => {
      const { result } = renderHook(() => useErrorHandler());

      const message = result.current.handleError('unknown error');
      expect(message).toBe('Erro desconhecido. Tente novamente.');
    });

    it('should handle null error', () => {
      const { result } = renderHook(() => useErrorHandler());

      const message = result.current.handleError(null);
      expect(message).toBe('Erro desconhecido. Tente novamente.');
    });
  });
});