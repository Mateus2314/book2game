import React from 'react';
import {StyleSheet, View} from 'react-native';
import {Card, Text, Chip, Avatar, ProgressBar} from 'react-native-paper';
import type {Game} from '../../types/api';
import {getGameIcon} from '../../utils/gameIcons';

interface GameCardProps {
  game: Game;
  similarityScore?: number;
  onPress?: () => void;
}

export function GameCard({game, similarityScore, onPress}: GameCardProps) {
  const icon = getGameIcon(game.genres);

  return (
    <Card style={styles.card} onPress={onPress} mode="elevated">
      <Card.Content>
        <View style={styles.header}>
          <Avatar.Icon size={48} icon={icon} style={styles.avatar} />
          <View style={styles.headerText}>
            <Text variant="titleMedium" numberOfLines={2} style={styles.title}>
              {game.name}
            </Text>
            {game.rating && (
              <View style={styles.rating}>
                <Text variant="bodySmall" style={styles.ratingText}>
                  ⭐ {game.rating.toFixed(1)}/5
                </Text>
                {game.metacritic && (
                  <Text variant="bodySmall" style={styles.metacritic}>
                    • Meta: {game.metacritic}
                  </Text>
                )}
              </View>
            )}
          </View>
        </View>

        {game.description && (
          <Text
            variant="bodySmall"
            numberOfLines={3}
            style={styles.description}>
            {game.description}
          </Text>
        )}

        {game.genres && game.genres.length > 0 && (
          <View style={styles.genres}>
            {game.genres.slice(0, 3).map((genre, index) => (
              <Chip key={index} mode="outlined" style={styles.chip} compact>
                {genre}
              </Chip>
            ))}
          </View>
        )}

        {similarityScore !== undefined && (
          <View style={styles.similarity}>
            <Text variant="bodySmall" style={styles.similarityLabel}>
              Similaridade: {(similarityScore * 100).toFixed(0)}%
            </Text>
            <ProgressBar
              progress={similarityScore}
              color="#6750A4"
              style={styles.progressBar}
            />
          </View>
        )}

        {game.released && (
          <Text variant="bodySmall" style={styles.released}>
            Lançamento: {new Date(game.released).getFullYear()}
          </Text>
        )}
      </Card.Content>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginVertical: 8,
    marginHorizontal: 16,
  },
  header: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  avatar: {
    backgroundColor: '#E7E0EC',
  },
  headerText: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'center',
  },
  title: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  rating: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    color: '#49454F',
  },
  metacritic: {
    color: '#79747E',
    marginLeft: 4,
  },
  description: {
    marginBottom: 12,
    color: '#1C1B1F',
  },
  genres: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  chip: {
    marginRight: 4,
    marginBottom: 4,
  },
  similarity: {
    marginBottom: 8,
  },
  similarityLabel: {
    color: '#49454F',
    marginBottom: 4,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
  },
  released: {
    color: '#79747E',
    marginTop: 4,
  },
});
