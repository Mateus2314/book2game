import {z} from 'zod';

export const loginSchema = z.object({
  email: z.string().min(1, 'Email é obrigatório').email('Email inválido'),
  password: z.string().min(8, 'Senha deve ter no mínimo 8 caracteres'),
});

export const registerSchema = z.object({
  email: z.string().min(1, 'Email é obrigatório').email('Email inválido'),
  password: z.string().min(8, 'Senha deve ter no mínimo 8 caracteres'),
  full_name: z
    .string()
    .min(1, 'Nome completo é obrigatório')
    .min(3, 'Nome deve ter no mínimo 3 caracteres'),
});

export const updateProfileSchema = z.object({
  email: z.string().min(1, 'Email é obrigatório').email('Email inválido'),
  full_name: z
    .string()
    .min(1, 'Nome completo é obrigatório')
    .min(3, 'Nome deve ter no mínimo 3 caracteres'),
  password: z
    .string()
    .min(8, 'Senha deve ter no mínimo 8 caracteres')
    .optional()
    .or(z.literal('')),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type UpdateProfileFormData = z.infer<typeof updateProfileSchema>;
