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
    mutationFn: usersApi.addGameToLibrary,
    onSuccess: () => {
      queryClient.invalidateQueries({queryKey: ['gameLibrary']});
      setSnackbarMessage('Jogo adicionado à biblioteca!');
      setTimeout(onDismiss, 1500);
    },
    onError: error => {
      setSnackbarMessage(handleError(error));
    },
  });

  if (!game) {
    return null;
  }

  const handleAddToLibrary = () => {
    addToLibraryMutation.mutate({
      game_id: game.id,
      play_status: 'to_play',
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
                {game.name}
              </Text>
              <IconButton icon="close" onPress={onDismiss} />
            </View>

            <ScrollView contentContainerStyle={styles.content}>
              {game.rating && (
                <View style={styles.rating}>
                  <Text variant="titleMedium">
                    ⭐ {game.rating.toFixed(1)}/5
                  </Text>
                  {game.metacritic && (
                    <Text variant="bodyMedium" style={styles.metacritic}>
                      Metacritic: {game.metacritic}
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
                  <Text variant="bodyMedium">{game.description}</Text>
                </View>
              )}

              {game.genres && game.genres.length > 0 && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Gêneros
                  </Text>
                  <View style={styles.chips}>
                    {game.genres.map((genre, index) => (
                      <Chip key={index} mode="outlined" style={styles.chip}>
                        {genre}
                      </Chip>
                    ))}
                  </View>
                </View>
              )}

              {game.tags && game.tags.length > 0 && (
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
                        {tag}
                      </Chip>
                    ))}
                  </View>
                </View>
              )}

              {game.platforms && game.platforms.length > 0 && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Plataformas
                  </Text>
                  <View style={styles.chips}>
                    {game.platforms.map((platform, index) => (
                      <Chip key={index} mode="flat" style={styles.chip}>
                        {platform}
                      </Chip>
                    ))}
                  </View>
                </View>
              )}

              {game.developers && game.developers.length > 0 && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Desenvolvedores
                  </Text>
                  <Text variant="bodyMedium">{game.developers.join(', ')}</Text>
                </View>
              )}

              {game.publishers && game.publishers.length > 0 && (
                <View style={styles.section}>
                  <Text variant="labelLarge" style={styles.label}>
                    Publishers
                  </Text>
                  <Text variant="bodyMedium">{game.publishers.join(', ')}</Text>
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
    gap: 8,
  },
  chip: {
    marginRight: 4,
    marginBottom: 4,
  },
  button: {
    marginTop: 16,
    paddingVertical: 8,
  },
});
