import React, {useState} from 'react';
import {ScrollView, StyleSheet, View} from 'react-native';
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
import {useMutation} from '@tanstack/react-query';
import {recommendationsApi} from '../../services/api/endpoints';
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
        <Text variant="headlineSmall" style={styles.title}>
          {book.title}
        </Text>

        {book.authors && book.authors.length > 0 && (
          <Text variant="titleMedium" style={styles.authors}>
            {book.authors.join(', ')}
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
              {book.categories.map((category, index) => (
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
              {book.description}
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
});
