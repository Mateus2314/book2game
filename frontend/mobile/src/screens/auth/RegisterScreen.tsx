import React, {useState} from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import {TextInput, Button, Text, Snackbar, Surface} from 'react-native-paper';
import {useForm, Controller} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {useMutation} from '@tanstack/react-query';
import {registerSchema, type RegisterFormData} from '../../schemas/authSchemas';
import {authApi} from '../../services/api/endpoints';
import {authStorage} from '../../services/auth/authStorage';
import {useAuthStore} from '../../stores/authStore';
import {useErrorHandler} from '../../hooks/useErrorHandler';
import type {AuthStackScreenProps} from '../../types/navigation';

export function RegisterScreen({navigation}: AuthStackScreenProps<'Register'>) {
  const [showPassword, setShowPassword] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const {handleError} = useErrorHandler();
  const setUser = useAuthStore(state => state.setUser);
  const setAuthenticated = useAuthStore(state => state.setAuthenticated);

  const {
    control,
    handleSubmit,
    formState: {errors},
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      full_name: '',
    },
  });

  const registerMutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: async data => {
      await authStorage.setTokens(
        data.access_token,
        data.refresh_token,
        data.user,
      );
      setUser(data.user);
      setAuthenticated(true);
    },
    onError: error => {
      setSnackbarMessage(handleError(error));
    },
  });

  const onSubmit = (data: RegisterFormData) => {
    registerMutation.mutate(data);
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Surface style={styles.surface}>
          <View style={styles.content}>
            <Text variant="displaySmall" style={styles.title}>
              Criar Conta
            </Text>
            <Text variant="bodyLarge" style={styles.subtitle}>
              Junte-se ao Book2Game
            </Text>

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
                  left={<TextInput.Icon icon="account" />}
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
                  left={<TextInput.Icon icon="email" />}
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
                  label="Senha"
                  mode="outlined"
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  error={!!errors.password}
                  secureTextEntry={!showPassword}
                  style={styles.input}
                  left={<TextInput.Icon icon="lock" />}
                  right={
                    <TextInput.Icon
                      icon={showPassword ? 'eye-off' : 'eye'}
                      onPress={() => setShowPassword(!showPassword)}
                    />
                  }
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
              loading={registerMutation.isPending}
              disabled={registerMutation.isPending}
              style={styles.button}>
              Criar Conta
            </Button>

            <Button
              mode="text"
              onPress={() => navigation.navigate('Login')}
              style={styles.loginButton}>
              Já tem uma conta? Entre
            </Button>
          </View>
        </Surface>
      </ScrollView>

      <Snackbar
        visible={!!snackbarMessage}
        onDismiss={() => setSnackbarMessage('')}
        duration={3000}
        action={{
          label: 'OK',
          onPress: () => setSnackbarMessage(''),
        }}>
        {snackbarMessage}
      </Snackbar>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
  },
  surface: {
    flex: 1,
    justifyContent: 'center',
  },
  content: {
    padding: 24,
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
    fontWeight: 'bold',
    color: '#6750A4',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 32,
    color: '#49454F',
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
  loginButton: {
    marginTop: 8,
  },
});
