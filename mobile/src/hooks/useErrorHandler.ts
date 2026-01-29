import {AxiosError} from 'axios';
import type {ApiError} from '../types/api';

export function useErrorHandler() {
  const handleError = (error: unknown): string => {
    if (error instanceof AxiosError) {
      const apiError = error.response?.data as ApiError;
      const status = error.response?.status;

      // Rate limiting
      if (status === 429) {
        return 'Limite de requisições atingido. Tente novamente em alguns minutos.';
      }

      // Unauthorized
      if (status === 401) {
        return 'Sessão expirada. Faça login novamente.';
      }

      // Not found
      if (status === 404) {
        return 'Recurso não encontrado.';
      }

      // Server error
      if (status && status >= 500) {
        return 'Erro no servidor. Tente novamente mais tarde.';
      }

      // Timeout
      if (error.code === 'ECONNABORTED') {
        return 'Tempo de resposta esgotado. Verifique sua conexão.';
      }

      // Network error
      if (!error.response) {
        return 'Erro de conexão. Verifique sua internet.';
      }

      // API error message
      if (apiError?.detail) {
        return apiError.detail;
      }

      // FastAPI/Pydantic validation error (array de objetos)
      if(Array.isArray(apiError)) {
        //Extrai todas as mensagens 'msg' e junta em uma única string
        return apiError.map(err => err.msg).join(' \n ');
      }
      //Caso venha um objeto com msg
      if(apiError?.msg) {
        return apiError.msg;
      }

      return 'Erro ao comunicar com a API. Tente novamente.';
    }

    if (error instanceof Error) {
      return error.message;
    }

    return 'Erro desconhecido. Tente novamente.';
  };

  return {handleError};
}
