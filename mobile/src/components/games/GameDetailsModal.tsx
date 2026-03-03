import React, {useState} from 'react';
import {ScrollView, StyleSheet, View} from 'react-native';
import {
  Portal,
  Modal,
  Text,
  Button,
  Chip,
  IconButton,
  Surface,
  Snackbar,
} from 'react-native-paper';
import {useMutation, useQueryClient} from '@tanstack/react-query';
import {usersApi} from '../../services/api/endpoints';
import {useErrorHandler} from '../../hooks/useErrorHandler';
import type {Game} from '../../types/api';

interface GameDetailsModalProps {
  game: Game | null;
  visible: boolean;
  onDismiss: () => void;
}

export function GameDetailsModal({
  game,
  visible,
  onDismiss,
}: GameDetailsModalProps) {
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const {handleError} = useErrorHandler();
  const queryClient = useQueryClient();

  const addToLibraryMutation = useMutation({
    mutationFn: (data: {game_id: number}) => {
      console.log('[GameDetailsModal] Adding game to library:', {
        gameId: data.game_id,
        gameName: game?.name,
        isGameValid: !!game && !!game.id,
      });
      return usersApi.addGameToLibrary(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({queryKey: ['gameLibrary']});
      setSnackbarMessage('Jogo adicionado à biblioteca!');
      console.log('[GameDetailsModal] Game added successfully');
      setTimeout(onDismiss, 1500);
    },
    onError: (error: any) => {
      console.error('[GameDetailsModal] Error adding game:', {
        error: error,
        errorMessage: error?.message || error?.response?.data?.detail,
        gameId: game?.id,
      });
      setSnackbarMessage(handleError(error));
    },
  });

  if (!game || !game.id) {
    return null;
  }

  // Debug logging
  console.log('[GameDetailsModal] Game data:', {
    id: game.id,
    name: game.name,
    hasGenres: 'genres' in game,
    genresType: typeof game.genres,
    genresIsArray: Array.isArray(game.genres),
    genresLength: game.genres?.length,
  });

  // Garantir que genres sempre seja um array
  const genresArray: string[] = (() => {
    if (Array.isArray(game.genres)) {
      return game.genres as string[];
    } else if (typeof game.genres === 'string') {
      return (game.genres as string).split(',').map((g: string) => g.trim()).filter((g: string) => g);
    }
    return [];
  })();

  const handleAddToLibrary = () => {
    console.log('[GameDetailsModal] handleAddToLibrary called with game.id:', game.id);
    if (!game || !game.id) {
      console.error('[GameDetailsModal] Game or game.id is invalid');
      setSnackbarMessage('Erro: Jogo inválido');
      return;
    }
    addToLibraryMutation.mutate({
      game_id: game.id,
    });
  };

  return (
    <>
      <Portal>
        <Modal
          visible={visible}
          onDismiss={onDismiss}
          contentContainerStyle={styles.modal}>
          <Surface style={styles.surface}>
            <View style={styles.header}>
              <Text variant="headlineSmall" style={styles.title}>
                {game.name ? String(game.name) : 'Sem nome'}
              </Text>
              <IconButton icon="close" onPress={onDismiss} />
            </View>

            <ScrollView contentContainerStyle={styles.content}>
              {game.rating && (
                <View style={styles.rating}>
                  <Text variant="titleMedium">
                    ⭐️ {Number(game.rating).toFixed(1)}/5
                  </Text>
                  {game.metacritic && (
                    <Text variant="bodyMedium" style={styles.metacritic}>
                      Metacritic: {String(game.metacritic)}
                    </Text>
                  )}
                </View>
              )}

              {game.released && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Lançamento
                  </Text>
                  <Text variant="bodyMedium">
                    {new Date(game.released).toLocaleDateString('pt-BR')}
                  </Text>
                </View>
              )}

              {game.description && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Descrição
                  </Text>
                  <Text variant="bodyMedium">{String(game.description).substring(0, 500)}</Text>
                </View>
              )}

              {genresArray && genresArray.length > 0 && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Gêneros
                  </Text>
                  <View style={styles.chips}>
                    {genresArray.map((genre: string, index: number) => (
                      <Chip key={index} mode="outlined" style={styles.chip}>
                        {String(genre).trim()}
                      </Chip>
                    ))}
                  </View>
                </View>
              )}

              {game.tags && Array.isArray(game.tags) && game.tags.length > 0 && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Tags
                  </Text>
                  <View style={styles.chips}>
                    {game.tags.slice(0, 10).map((tag, index) => (
                      <Chip
                        key={index}
                        mode="outlined"
                        style={styles.chip}
                        compact>
                        {String(tag).trim()}
                      </Chip>
                    ))}
                  </View>
                </View>
              )}

              {game.platforms && Array.isArray(game.platforms) && game.platforms.length > 0 && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Plataformas
                  </Text>
                  <View style={styles.chips}>
                    {game.platforms.map((platform, index) => (
                      <Chip key={index} mode="flat" style={styles.chip}>
                        {String(platform).trim()}
                      </Chip>
                    ))}
                  </View>
                </View>
              )}

              {game.developers && Array.isArray(game.developers) && game.developers.length > 0 && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Desenvolvedores
                  </Text>
                  <Text variant="bodyMedium">{game.developers.map(d => String(d)).join(', ')}</Text>
                </View>
              )}

              {game.publishers && Array.isArray(game.publishers) && game.publishers.length > 0 && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Publishers
                  </Text>
                  <Text variant="bodyMedium">{game.publishers.map(p => String(p)).join(', ')}</Text>
                </View>
              )}

              <Button
                mode="contained"
                icon="plus"
                onPress={handleAddToLibrary}
                loading={addToLibraryMutation.isPending}
                disabled={addToLibraryMutation.isPending}
                style={styles.button}>
                Adicionar à Biblioteca
              </Button>
            </ScrollView>
          </Surface>
        </Modal>
      </Portal>

      <Snackbar
        visible={!!snackbarMessage}
        onDismiss={() => setSnackbarMessage('')}
        duration={3000}>
        {snackbarMessage}
      </Snackbar>
    </>
  );
}

const styles = StyleSheet.create({
  modal: {
    margin: 20,
    maxHeight: '90%',
  },
  surface: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#F3EDF7',
  },
  title: {
    flex: 1,
    fontWeight: 'bold',
  },
  content: {
    padding: 16,
  },
  rating: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  metacritic: {
    marginLeft: 16,
    color: '#49454F',
  },
  section: {
    marginBottom: 16,
  },
  label: {
    marginBottom: 8,
    color: '#6750A4',
  },
  chips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -4,
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
  button: {
    marginTop: 16,
    paddingVertical: 8,
  },
});
