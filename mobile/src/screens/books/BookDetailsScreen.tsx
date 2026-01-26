import React, {useState, useMemo} from 'react';
import {ScrollView, StyleSheet, View, TouchableOpacity} from 'react-native';
import {
  Text,
  Button,
  Chip,
  Surface,
  Portal,
  Dialog,
  ActivityIndicator,
  Snackbar,
} from 'react-native-paper';
// @ts-ignore
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import Animated, {useSharedValue, useAnimatedStyle, withSpring} from 'react-native-reanimated';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import {recommendationsApi, usersApi} from '../../services/api/endpoints';
import {useErrorHandler} from '../../hooks/useErrorHandler';
import type {HomeStackScreenProps} from '../../types/navigation';

export function BookDetailsScreen({
  route,
  navigation,
}: HomeStackScreenProps<'BookDetails'>) {
  const {book} = route.params;
  const [dialogVisible, setDialogVisible] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const {handleError} = useErrorHandler();
  const queryClient = useQueryClient();

  // Busca biblioteca do usuário para saber se o livro está nela
  const {data: userBooks = [], isLoading: userBooksLoading} = useQuery({
    queryKey: ['bookLibrary'],
    queryFn: () => usersApi.getBookLibrary(),
  });

  // Função para checar se o livro está na biblioteca
  const isInLibrary = useMemo(() =>
    userBooks.some((ub: any) => ub.book?.google_books_id === book.google_books_id),
    [userBooks, book.google_books_id]
  );
  // Busca o UserBook correspondente
  const userBook = useMemo(() =>
    userBooks.find((ub: any) => ub.book?.google_books_id === book.google_books_id),
    [userBooks, book.google_books_id]
  );

  // Animação do botão
  const scale = useSharedValue(1);
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{scale: scale.value}],
  }));

  // Mutations para adicionar/remover
  const addMutation = useMutation({
    mutationFn: () => usersApi.addBookToLibrary({google_books_id: book.google_books_id}),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['bookLibrary'] });
      setSnackbarMessage('Livro adicionado à biblioteca!');
    },
    onError: error => setSnackbarMessage(handleError(error)),
  });
  const removeMutation = useMutation({
    mutationFn: () => usersApi.removeBookFromLibrary(userBook?.book_id ?? book.id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['bookLibrary'] });
      setSnackbarMessage('Livro removido da biblioteca!');
    },
    onError: error => setSnackbarMessage(handleError(error)),
  });

  const handleLibraryToggle = async () => {
    scale.value = withSpring(1.2, { damping: 10, stiffness: 200 }, () => {
      scale.value = withSpring(1);
    });
    if (isInLibrary) {
      removeMutation.mutate();
    } else {
      addMutation.mutate();
    }
  };

  const recommendationMutation = useMutation({
    mutationFn: recommendationsApi.create,
    onSuccess: recommendation => {
      setDialogVisible(false);
      navigation.navigate('RecommendationResults', {recommendation});
    },
    onError: error => {
      setDialogVisible(false);
      setSnackbarMessage(handleError(error));
    },
  });

  const handleGetRecommendations = () => {
    setDialogVisible(true);
    recommendationMutation.mutate({google_books_id: book.google_books_id});
  };

  return (
    <Surface style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.headerRow}>
          <Text variant="headlineSmall" style={styles.title}>
            {book.title}
          </Text>
          <Animated.View style={animatedStyle}>
            <TouchableOpacity
              onPress={handleLibraryToggle}
              disabled={addMutation.isPending || removeMutation.isPending || userBooksLoading}
              style={styles.bookmarkButton}>
              <MaterialCommunityIcons
                name={isInLibrary ? 'bookmark-check' : 'bookmark-plus-outline'}
                size={32}
                color={isInLibrary ? '#1976d2' : '#aaa'}
              />
            </TouchableOpacity>
          </Animated.View>
        </View>

        {book.authors && book.authors.length > 0 && (
          <Text variant="titleMedium" style={styles.authors}>
            {Array.isArray(book.authors) ? book.authors.join(', ') : book.authors}
          </Text>
        )}

        <View style={styles.metadata}>
          {book.published_date && (
            <View style={styles.metadataItem}>
              <Text variant="bodySmall" style={styles.metadataLabel}>
                Publicado:
              </Text>
              <Text variant="bodyMedium">
                {new Date(book.published_date).getFullYear()}
              </Text>
            </View>
          )}

          {book.publisher && (
            <View style={styles.metadataItem}>
              <Text variant="bodySmall" style={styles.metadataLabel}>
                Editora:
              </Text>
              <Text variant="bodyMedium">{book.publisher}</Text>
            </View>
          )}

          {book.page_count && (
            <View style={styles.metadataItem}>
              <Text variant="bodySmall" style={styles.metadataLabel}>
                Páginas:
              </Text>
              <Text variant="bodyMedium">{book.page_count}</Text>
            </View>
          )}

          {book.language && (
            <View style={styles.metadataItem}>
              <Text variant="bodySmall" style={styles.metadataLabel}>
                Idioma:
              </Text>
              <Text variant="bodyMedium">{book.language.toUpperCase()}</Text>
            </View>
          )}
        </View>

        {book.categories && book.categories.length > 0 && (
          <View style={styles.section}>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Categorias
            </Text>
            <View style={styles.categories}>
              {(Array.isArray(book.categories) ? book.categories : String(book.categories).split(',')).map((category, index) => (
                <Chip key={index} mode="outlined" style={styles.chip}>
                  {category}
                </Chip>
              ))}
            </View>
          </View>
        )}

        {book.description && (
          <View style={styles.section}>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Descrição
            </Text>
            <Text variant="bodyMedium" style={styles.description}>
              {typeof book.description === 'string' ? book.description.replace(/<[^>]+>/g, '') : ''}
            </Text>
          </View>
        )}

        {(book.isbn_10 || book.isbn_13) && (
          <View style={styles.section}>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              ISBN
            </Text>
            {book.isbn_13 && (
              <Text variant="bodyMedium">ISBN-13: {book.isbn_13}</Text>
            )}
            {book.isbn_10 && (
              <Text variant="bodyMedium">ISBN-10: {book.isbn_10}</Text>
            )}
          </View>
        )}

        <Button
          mode="contained"
          icon="gamepad-variant"
          onPress={handleGetRecommendations}
          disabled={recommendationMutation.isPending}
          style={styles.button}>
          Obter Recomendações de Jogos
        </Button>
      </ScrollView>

      <Portal>
        <Dialog visible={dialogVisible} dismissable={false}>
          <Dialog.Content style={styles.dialogContent}>
            <ActivityIndicator size="large" />
            <Text variant="titleMedium" style={styles.dialogText}>
              Gerando recomendações com IA Llama 3.1...
            </Text>
            <Text variant="bodySmall" style={styles.dialogSubtext}>
              Isso pode levar de 5 a 10 segundos
            </Text>
          </Dialog.Content>
        </Dialog>
      </Portal>

      <Snackbar
        visible={!!snackbarMessage}
        onDismiss={() => setSnackbarMessage('')}
        duration={4000}
        action={{
          label: 'OK',
          onPress: () => setSnackbarMessage(''),
        }}>
        {snackbarMessage}
      </Snackbar>
    </Surface>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  title: {
    fontWeight: 'bold',
    marginBottom: 8,
  },
  authors: {
    color: '#49454F',
    marginBottom: 16,
  },
  metadata: {
    backgroundColor: '#F3EDF7',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  metadataItem: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  metadataLabel: {
    color: '#49454F',
    width: 80,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontWeight: 'bold',
    marginBottom: 12,
  },
  categories: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
  description: {
    lineHeight: 24,
  },
  button: {
    marginTop: 16,
    paddingVertical: 8,
  },
  dialogContent: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  dialogText: {
    marginTop: 16,
    textAlign: 'center',
  },
  dialogSubtext: {
    marginTop: 8,
    textAlign: 'center',
    color: '#79747E',
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  bookmarkButton: {
    marginLeft: 8,
  },
});
