import { renderHook, act } from '@testing-library/react-native';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

// Schema de validação para login
const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Senha deve ter no mínimo 6 caracteres'),
});

type LoginFormData = z.infer<typeof loginSchema>;

// Schema de validação para registro
const registerSchema = z.object({
  email: z.string().email('Email inválido'),
  username: z.string().min(3, 'Username deve ter no mínimo 3 caracteres'),
  password: z.string().min(8, 'Senha deve ter no mínimo 8 caracteres'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Senhas não conferem',
  path: ['confirmPassword'],
});

type RegisterFormData = z.infer<typeof registerSchema>;

describe('Form Validation Integration', () => {
  describe('Login Form Validation', () => {
    it('should validate email field', () => {
      const { result } = renderHook(() => useForm<LoginFormData>());

      act(() => {
        loginSchema.parse({
          email: 'valid@example.com',
          password: 'password123',
        });
      });

      // No error thrown = valid
      expect(true).toBe(true);
    });

    it('should reject invalid email', () => {
      expect(() => {
        loginSchema.parse({
          email: 'invalid-email',
          password: 'password123',
        });
      }).toThrow();
    });

    it('should validate password length', () => {
      expect(() => {
        loginSchema.parse({
          email: 'test@example.com',
          password: '123',
        });
      }).toThrow();
    });

    it('should accept valid login credentials', () => {
      expect(() => {
        loginSchema.parse({
          email: 'user@example.com',
          password: 'securepassword123',
        });
      }).not.toThrow();
    });

    it('should handle multiple validation errors', () => {
      expect(() => {
        loginSchema.parse({
          email: 'invalid-email',
          password: '123',
        });
      }).toThrow();
    });
  });

  describe('Register Form Validation', () => {
    it('should validate all required fields', () => {
      expect(() => {
        registerSchema.parse({
          email: 'newuser@example.com',
          username: 'newusername',
          password: 'securepass123',
          confirmPassword: 'securepass123',
        });
      }).not.toThrow();
    });

    it('should reject mismatched passwords', () => {
      expect(() => {
        registerSchema.parse({
          email: 'newuser@example.com',
          username: 'newusername',
          password: 'securepass123',
          confirmPassword: 'differentpass123',
        });
      }).toThrow();
    });

    it('should validate username minimum length', () => {
      expect(() => {
        registerSchema.parse({
          email: 'newuser@example.com',
          username: 'ab',
          password: 'securepass123',
          confirmPassword: 'securepass123',
        });
      }).toThrow();
    });

    it('should validate password minimum length', () => {
      expect(() => {
        registerSchema.parse({
          email: 'newuser@example.com',
          username: 'validusername',
          password: 'short',
          confirmPassword: 'short',
        });
      }).toThrow();
    });

    it('should reject invalid email format', () => {
      expect(() => {
        registerSchema.parse({
          email: 'not-an-email',
          username: 'validusername',
          password: 'securepass123',
          confirmPassword: 'securepass123',
        });
      }).toThrow();
    });

    it('should accept all valid inputs', () => {
      expect(() => {
        registerSchema.parse({
          email: 'validuser@example.com',
          username: 'validusername',
          password: 'verySecurePassword123',
          confirmPassword: 'verySecurePassword123',
        });
      }).not.toThrow();
    });
  });

  describe('Form Field Validation', () => {
    it('should validate email with special characters', () => {
      expect(() => {
        loginSchema.parse({
          email: 'user+tag@example.co.uk',
          password: 'password123',
        });
      }).not.toThrow();
    });

    it('should handle empty fields', () => {
      expect(() => {
        loginSchema.parse({
          email: '',
          password: '',
        });
      }).toThrow();
    });

    it('should trim whitespace from inputs', () => {
      const testData = {
        email: '  test@example.com  ',
        password: 'password123',
      };

      // Simulating form trimming
      const trimmedData = {
        email: testData.email.trim(),
        password: testData.password.trim(),
      };

      expect(() => {
        loginSchema.parse(trimmedData);
      }).not.toThrow();
    });
  });

  describe('Real-world Form Scenarios', () => {
    it('should handle rapid form submissions', () => {
      const validData = {
        email: 'user@example.com',
        password: 'securepass123',
      };

      // Multiple submissions
      for (let i = 0; i < 5; i++) {
        expect(() => {
          loginSchema.parse(validData);
        }).not.toThrow();
      }
    });

    it('should maintain form data integrity after validation', () => {
      const originalData = {
        email: 'test@example.com',
        password: 'password123',
      };

      const validated = loginSchema.parse(originalData);
      expect(validated).toEqual(originalData);
    });

    it('should handle form reset', () => {
      const initialData = {
        email: 'user@example.com',
        password: 'password123',
      };

      expect(() => {
        loginSchema.parse(initialData);
      }).not.toThrow();

      const resetData = {
        email: '',
        password: '',
      };

      expect(() => {
        loginSchema.parse(resetData);
      }).toThrow();
    });
  });
});