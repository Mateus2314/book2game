import React, {useState} from 'react';
import {FlatList, StyleSheet, View} from 'react-native';
import {Text, Surface} from 'react-native-paper';
import {useQuery} from '@tanstack/react-query';
import {gamesApi} from '../../services/api/endpoints';
import {GameCard} from '../../components/games/GameCard';
import {GameDetailsModal} from '../../components/games/GameDetailsModal';
import type {LibraryStackScreenProps} from '../../types/navigation';

type RecommendationResultsScreenProps = LibraryStackScreenProps<'RecommendationResults'>;
import type {Game} from '../../types/api';


export function RecommendationResultsScreen({ route }: RecommendationResultsScreenProps) {
  const {recommendation} = route.params;
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);

  // Garante que games sempre será um array
  const gamesList = recommendation.games ?? recommendation.recommended_games ?? [];

  const {data: games = []} = useQuery({
    queryKey: ['games', gamesList.map(g => g.game_id)],
    queryFn: async () => {
      try {
        const gamePromises = gamesList.map(g =>
          gamesApi.getById(g.game_id).catch(error => {
            console.error(`Erro ao buscar jogo ${g.game_id}:`, error);
            return null;
          }),
        );
        const results = await Promise.all(gamePromises);
        return results.filter((game): game is Game => game !== null);
      } catch (error) {
        console.error('Erro ao buscar jogos:', error);
        return [];
      }
    },
  });

  const gamesWithScores = games
    .filter(game => game && game.id) // Filtrar jogos inválidos
    .map((game) => ({
      game,
      score: gamesList.find(g => g.game_id === game.id)?.score || 0,
    }));

  const renderItem = ({item}: {item: {game: Game; score: number}}) => (
    <GameCard
      game={item.game}
      similarityScore={item.score}
      onPress={() => setSelectedGame(item.game)}
    />
  );

  return (
    <Surface style={styles.container}>
      <View style={styles.header}>
        <Text variant="titleLarge" style={styles.title}>
          Jogos Recomendados
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          {games.length} jogos encontrados para "{recommendation.book?.title}"
        </Text>
      </View>

      <FlatList
        data={gamesWithScores}
        renderItem={renderItem}
        keyExtractor={item => item.game.id.toString()}
        contentContainerStyle={styles.list}
      />

      <GameDetailsModal
        game={selectedGame}
        visible={!!selectedGame}
        onDismiss={() => setSelectedGame(null)}
      />
    </Surface>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 16,
    backgroundColor: '#F3EDF7',
  },
  title: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  subtitle: {
    color: '#49454F',
  },
  list: {
    paddingVertical: 8,
  },
});
