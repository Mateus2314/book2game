import React, {useState} from 'react';
import {FlatList, StyleSheet, View} from 'react-native';
import {Surface, SegmentedButtons, ActivityIndicator} from 'react-native-paper';
import {useQuery} from '@tanstack/react-query';
import {usersApi} from '../../services/api/endpoints';
import {BookCard} from '../../components/books/BookCard';
import {GameCard} from '../../components/games/GameCard';
import {EmptyState} from '../../components/common/EmptyState';

export function LibraryScreen() {
  const [tab, setTab] = useState('books');

  const {data: books = [], isLoading: booksLoading} = useQuery({
    queryKey: ['bookLibrary'],
    queryFn: () => usersApi.getBookLibrary(),
    enabled: tab === 'books',
  });

  const {data: games = [], isLoading: gamesLoading} = useQuery({
    queryKey: ['gameLibrary'],
    queryFn: () => usersApi.getGameLibrary(),
    enabled: tab === 'games',
  });

  const isLoading = tab === 'books' ? booksLoading : gamesLoading;
  const data = tab === 'books' ? books : games;

  const renderItem = ({item}: {item: any}) => {
    if (tab === 'books') {
      return <BookCard book={item.book} inLibrary={true} />;
    }
    return <GameCard game={item.game} />;
  };

  const renderEmpty = () => {
    if (isLoading) {
      return (
        <View style={styles.loading}>
          <ActivityIndicator size="large" />
        </View>
      );
    }

    return (
      <EmptyState
        icon={tab === 'books' ? 'book-open-blank-variant' : 'gamepad-variant'}
        title={`Nenhum ${tab === 'books' ? 'livro' : 'jogo'} na biblioteca`}
        description={`Adicione ${
          tab === 'books' ? 'livros' : 'jogos'
        } às suas coleções`}
      />
    );
  };

  return (
    <Surface style={styles.container}>
      <SegmentedButtons
        value={tab}
        onValueChange={setTab}
        buttons={[
          {value: 'books', label: 'Livros', icon: 'book'},
          {value: 'games', label: 'Jogos', icon: 'gamepad-variant'},
        ]}
        style={styles.tabs}
      />
      <FlatList
        data={data}
        renderItem={renderItem}
        keyExtractor={(item: any) => item.id.toString()}
        ListEmptyComponent={renderEmpty}
        contentContainerStyle={
          data.length === 0 ? styles.emptyContainer : styles.list
        }
      />
    </Surface>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  tabs: {
    margin: 16,
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
  },
  list: {
    paddingBottom: 16,
  },
});
