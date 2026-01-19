import React, {useState} from 'react';
import {FlatList, StyleSheet, View} from 'react-native';
import {Text, Surface} from 'react-native-paper';
import {useQuery} from '@tanstack/react-query';
import {gamesApi} from '../../services/api/endpoints';
import {GameCard} from '../../components/games/GameCard';
import {GameDetailsModal} from '../../components/games/GameDetailsModal';
import type {HomeStackScreenProps} from '../../types/navigation';
import type {Game} from '../../types/api';

export function RecommendationResultsScreen({
  route,
}: HomeStackScreenProps<'RecommendationResults'>) {
  const {recommendation} = route.params;
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);

  const {data: games = []} = useQuery({
    queryKey: ['games', recommendation.games.map(g => g.game_id)],
    queryFn: async () => {
      const gamePromises = recommendation.games.map(g =>
        gamesApi.getById(g.game_id),
      );
      return await Promise.all(gamePromises);
    },
  });

  const gamesWithScores = games.map((game, index) => ({
    game,
    score: recommendation.games[index]?.score || 0,
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
