import React, {useState} from 'react';
import {FlatList, StyleSheet, View} from 'react-native';
import {Searchbar, ActivityIndicator, Surface} from 'react-native-paper';
import {useInfiniteQuery} from '@tanstack/react-query';
import {booksApi} from '../../services/api/endpoints';
import {BookCard} from '../../components/books/BookCard';
import {EmptyState} from '../../components/common/EmptyState';
import {useDebounce} from '../../hooks/useDebounce';
import type {HomeStackScreenProps} from '../../types/navigation';
import type {Book} from '../../types/api';

export function HomeScreen({navigation}: HomeStackScreenProps<'HomeScreen'>) {
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedQuery = useDebounce(searchQuery, 500);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    refetch,
  } = useInfiniteQuery({
    queryKey: ['books', debouncedQuery],
    queryFn: ({pageParam = 1}) => booksApi.search(debouncedQuery, pageParam),
    getNextPageParam: (lastPage, allPages) => {
      if (lastPage.items.length === 0) {
        return undefined;
      }
      return allPages.length + 1;
    },
    enabled: debouncedQuery.length > 0,
    initialPageParam: 1,
  });

  const books = data?.pages.flatMap(page => page.items) ?? [];

  const renderItem = ({item}: {item: Book}) => (
    <BookCard
      book={item}
      onPress={() => navigation.navigate('BookDetails', {book: item})}
    />
  );

  const renderFooter = () => {
    if (!isFetchingNextPage) {
      return null;
    }
    return (
      <View style={styles.footer}>
        <ActivityIndicator size="small" />
      </View>
    );
  };

  const renderEmpty = () => {
    if (isLoading) {
      return (
        <View style={styles.loading}>
          <ActivityIndicator size="large" />
        </View>
      );
    }

    if (debouncedQuery.length === 0) {
      return (
        <EmptyState
          icon="magnify"
          title="Busque por livros"
          description="Digite o nome de um livro para começar a busca"
        />
      );
    }

    return (
      <EmptyState
        icon="book-off"
        title="Nenhum livro encontrado"
        description="Tente buscar com outros termos"
      />
    );
  };

  const handleLoadMore = () => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  };

  return (
    <Surface style={styles.container}>
      <Searchbar
        placeholder="Buscar livros..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />
      <FlatList
        data={books}
        renderItem={renderItem}
        keyExtractor={(item, index) => `${item.id}-${index}`}
        ListEmptyComponent={renderEmpty}
        ListFooterComponent={renderFooter}
        onEndReached={handleLoadMore}
        onEndReachedThreshold={0.5}
        refreshing={false}
        onRefresh={refetch}
        contentContainerStyle={
          books.length === 0 ? styles.emptyContainer : undefined
        }
      />
    </Surface>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  searchbar: {
    margin: 16,
    elevation: 2,
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  emptyContainer: {
    flex: 1,
  },
  footer: {
    paddingVertical: 20,
    alignItems: 'center',
  },
});
