import React, {useState} from 'react';
import {
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {Surface, TextInput, Button, Text, Snackbar} from 'react-native-paper';
import {useForm, Controller} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {useMutation, useQueryClient} from '@tanstack/react-query';
import {
  updateProfileSchema,
  type UpdateProfileFormData,
} from '../../schemas/authSchemas';
import {usersApi} from '../../services/api/endpoints';
import {useAuthStore} from '../../stores/authStore';
import {useErrorHandler} from '../../hooks/useErrorHandler';
import type {ProfileStackScreenProps} from '../../types/navigation';

export function EditProfileScreen({
  navigation,
}: ProfileStackScreenProps<'EditProfile'>) {
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const {handleError} = useErrorHandler();
  const user = useAuthStore(state => state.user);
  const setUser = useAuthStore(state => state.setUser);
  const queryClient = useQueryClient();

  const {
    control,
    handleSubmit,
    formState: {errors},
  } = useForm<UpdateProfileFormData>({
    resolver: zodResolver(updateProfileSchema),
    defaultValues: {
      email: user?.email || '',
      full_name: user?.full_name || '',
      password: '',
    },
  });

  const updateMutation = useMutation({
    mutationFn: usersApi.updateMe,
    onSuccess: data => {
      setUser(data);
      queryClient.invalidateQueries({queryKey: ['user']});
      setSnackbarMessage('Perfil atualizado com sucesso!');
      setTimeout(() => navigation.goBack(), 1500);
    },
    onError: error => {
      setSnackbarMessage(handleError(error));
    },
  });

  const onSubmit = (data: UpdateProfileFormData) => {
    const payload: any = {
      email: data.email,
      full_name: data.full_name,
    };
    if (data.password && data.password.length >= 8) {
      payload.password = data.password;
    }
    updateMutation.mutate(payload);
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}>
      <Surface style={styles.surface}>
        <ScrollView contentContainerStyle={styles.content}>
          <Controller
            control={control}
            name="full_name"
            render={({field: {onChange, onBlur, value}}) => (
              <TextInput
                label="Nome Completo"
                mode="outlined"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                error={!!errors.full_name}
                style={styles.input}
              />
            )}
          />
          {errors.full_name && (
            <Text variant="bodySmall" style={styles.error}>
              {errors.full_name.message}
            </Text>
          )}

          <Controller
            control={control}
            name="email"
            render={({field: {onChange, onBlur, value}}) => (
              <TextInput
                label="Email"
                mode="outlined"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                error={!!errors.email}
                keyboardType="email-address"
                autoCapitalize="none"
                style={styles.input}
              />
            )}
          />
          {errors.email && (
            <Text variant="bodySmall" style={styles.error}>
              {errors.email.message}
            </Text>
          )}

          <Controller
            control={control}
            name="password"
            render={({field: {onChange, onBlur, value}}) => (
              <TextInput
                label="Nova Senha (opcional)"
                mode="outlined"
                value={value}
                onChangeText={onChange}
                onBlur={onBlur}
                error={!!errors.password}
                secureTextEntry
                style={styles.input}
              />
            )}
          />
          {errors.password && (
            <Text variant="bodySmall" style={styles.error}>
              {errors.password.message}
            </Text>
          )}

          <Button
            mode="contained"
            onPress={handleSubmit(onSubmit)}
            loading={updateMutation.isPending}
            disabled={updateMutation.isPending}
            style={styles.button}>
            Salvar Alterações
          </Button>
        </ScrollView>
      </Surface>

      <Snackbar
        visible={!!snackbarMessage}
        onDismiss={() => setSnackbarMessage('')}
        duration={3000}>
        {snackbarMessage}
      </Snackbar>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  surface: {
    flex: 1,
  },
  content: {
    padding: 24,
  },
  input: {
    marginBottom: 8,
  },
  error: {
    color: '#B3261E',
    marginBottom: 8,
    marginLeft: 12,
  },
  button: {
    marginTop: 16,
    paddingVertical: 8,
  },
});
