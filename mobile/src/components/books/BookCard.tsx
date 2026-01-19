import React from 'react';
import {StyleSheet, View} from 'react-native';
import {Card, Text, Chip} from 'react-native-paper';
import type {Book} from '../../types/api';

interface BookCardProps {
  book: Book;
  onPress?: () => void;
}

export function BookCard({book, onPress}: BookCardProps) {
  return (
    <Card style={styles.card} onPress={onPress} mode="elevated">
      <Card.Content>
        <Text variant="titleMedium" numberOfLines={2} style={styles.title}>
          {book.title}
        </Text>

        {book.authors && book.authors.length > 0 && (
          <Text variant="bodySmall" style={styles.authors} numberOfLines={1}>
            {book.authors.join(', ')}
          </Text>
        )}

        {book.description && (
          <Text
            variant="bodySmall"
            numberOfLines={3}
            style={styles.description}>
            {book.description}
          </Text>
        )}

        {book.categories && book.categories.length > 0 && (
          <View style={styles.categories}>
            {book.categories.slice(0, 3).map((category, index) => (
              <Chip key={index} mode="outlined" style={styles.chip} compact>
                {category}
              </Chip>
            ))}
          </View>
        )}

        <View style={styles.footer}>
          {book.published_date && (
            <Text variant="bodySmall" style={styles.date}>
              {new Date(book.published_date).getFullYear()}
            </Text>
          )}
          {book.page_count && (
            <Text variant="bodySmall" style={styles.pages}>
              {book.page_count} páginas
            </Text>
          )}
        </View>
      </Card.Content>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginVertical: 8,
    marginHorizontal: 16,
  },
  title: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  authors: {
    color: '#49454F',
    marginBottom: 8,
  },
  description: {
    marginBottom: 12,
    color: '#1C1B1F',
  },
  categories: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
  },
  chip: {
    marginRight: 4,
    marginBottom: 4,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  date: {
    color: '#79747E',
  },
  pages: {
    color: '#79747E',
  },
});
