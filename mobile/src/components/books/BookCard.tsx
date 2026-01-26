import React, {useState} from 'react';
import {StyleSheet, View, TouchableOpacity, Image} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import {Card, Text, Chip} from 'react-native-paper';
// Corrige aviso de tipo para MaterialCommunityIcons
// @ts-ignore
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import Animated, {useSharedValue, useAnimatedStyle, withSpring, FadeIn} from 'react-native-reanimated';
import Sound from 'react-native-sound';
import {usersApi} from '../../services/api/endpoints';
import type {Book} from '../../types/api';

interface BookCardProps {
  book: Book;
  userBookId?: number; // id da relação UserBook
  onPress?: () => void;
  inLibrary?: boolean;
  onLibraryChange?: (added: boolean) => void;
}

export function BookCard({book, userBookId, onPress, inLibrary, onLibraryChange}: BookCardProps) {
  
  // Normaliza authors para array
  const authorsArray: string[] = Array.isArray(book.authors)
    ? book.authors
    : typeof book.authors === 'string'
      ? book.authors.split(',').map((a: string) => a.trim())
      : [];
  // Normaliza categories para array de strings separadas
  let categoriesArray: string[] = [];
  if (Array.isArray(book.categories)) {
    categoriesArray = book.categories;
  } else if (typeof book.categories === 'string') {
    categoriesArray = book.categories.split(',').map((c: string) => c.trim());
  }
  // Debug detalhado
  console.log('[BookCard] DEBUG book.title:', book.title);
  console.log('[BookCard] book.categories:', book.categories, '| typeof:', typeof book.categories);
  console.log('[BookCard] categoriesArray:', categoriesArray);

  React.useEffect(() => {
    console.log('[BookCard] Render:', book.title, 'inLibrary:', inLibrary);
  }, [inLibrary]);
  
  const [loading, setLoading] = useState(false);
  const scale = useSharedValue(1);

  // Sons
  const addSound = new Sound('add.mp3', Sound.MAIN_BUNDLE, () => {});
  const removeSound = new Sound('remove.mp3', Sound.MAIN_BUNDLE, () => {});

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{scale: scale.value}],
  }));

  const handleLibraryToggle = async () => {
    console.log('[BookCard] Botão pressionado. inLibrary:', inLibrary, 'book:', book);
    setLoading(true);
    scale.value = withSpring(1.2, { damping: 10, stiffness: 200 }, () => {
      scale.value = withSpring(1);
    });
    try {
      if (inLibrary) {
        // Usa o userBookId se disponível, senão book.id (fallback)
        const idToRemove = userBookId ?? book.id;
        console.log('[BookCard] Removendo livro da biblioteca:', idToRemove);
        const resp = await usersApi.removeBookFromLibrary(idToRemove);
        console.log('[BookCard] Resposta removeBookFromLibrary:', resp);
        removeSound.play();
        onLibraryChange && onLibraryChange(false);
      } else {
        console.log('[BookCard] Adicionando livro à biblioteca:', book.google_books_id);
        const resp = await usersApi.addBookToLibrary({google_books_id: book.google_books_id});
        console.log('[BookCard] Resposta addBookToLibrary:', resp);
        addSound.play();
        onLibraryChange && onLibraryChange(true);
      }
    } catch (err) {
      console.log('[BookCard] Erro ao adicionar/remover livro:', err);
      // TODO: feedback de erro
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card style={styles.card} onPress={onPress} mode="elevated">
      <View style={styles.cardBg}>
        <Card.Content style={{flexDirection: 'row', alignItems: 'flex-start', padding: 0}}>
          {book.image_url && (
            <Animated.View entering={FadeIn} style={styles.coverShadow}>
              <Image
                source={{ uri: book.image_url }}
                style={styles.cover}
                resizeMode="cover"
              />
            </Animated.View>
          )}
          <View style={styles.infoArea}>
            <Text variant="titleLarge" numberOfLines={2} style={styles.title}>{String(book.title)}</Text>
            {book.authors && Array.isArray(book.authors) && book.authors.length > 0 ? (
              <Text variant="bodySmall" style={styles.authors} numberOfLines={1}>{book.authors.join(', ')}</Text>
            ) : null}
            {typeof book.description === 'string' && book.description !== '' ? (
              <Text variant="bodySmall" numberOfLines={2} style={styles.description}>{book.description.replace(/<[^>]*>/g, '')}</Text>
            ) : null}
            {book.categories && book.categories.length > 0 && (
              <View style={styles.categories}>
                {book.categories.slice(0, 2).map((category, index) => {
                  if (category != null && category !== '' && (typeof category === 'string' || typeof category === 'number')) {
                    return (
                      <Chip
                        key={index}
                        mode="flat"
                        style={styles.chip}
                        textStyle={{ color: '#1976d2', fontWeight: '600', fontSize: 12 }}
                        compact
                      >
                        {String(category)}
                      </Chip>
                    );
                  }
                  return null;
                })}
              </View>
            )}
            <View style={styles.footerRow}>
              {typeof book.published_date === 'string' && book.published_date !== '' ? (
                <View style={styles.footerItem}>
                  <MaterialCommunityIcons name="calendar" size={15} color="#90caf9" style={{marginRight: 2}} />
                  <Text variant="bodySmall" style={styles.date}>
                    {book.published_date.length === 4
                      ? book.published_date
                      : new Date(book.published_date).getFullYear()}
                  </Text>
                </View>
              ) : null}
              {typeof book.page_count === 'number' ? (
                <View style={styles.footerItem}>
                  <MaterialCommunityIcons name="book-open-page-variant" size={15} color="#b0bec5" style={{marginRight: 2}} />
                  <Text variant="bodySmall" style={styles.pages}>
                    {book.page_count} páginas
                  </Text>
                </View>
              ) : null}
            </View>
          </View>
          <Animated.View style={[animatedStyle, styles.actionButtonArea]}>
            <TouchableOpacity
              onPress={handleLibraryToggle}
              disabled={loading}
              accessibilityLabel={inLibrary ? 'Remover da biblioteca' : 'Adicionar à biblioteca'}
              style={styles.iconButton}
            >
              <MaterialCommunityIcons
                name={inLibrary ? 'bookmark-check' : 'bookmark-plus'}
                size={22}
                color={inLibrary ? '#1976d2' : '#b0bec5'}
              />
            </TouchableOpacity>
          </Animated.View>
        </Card.Content>
      </View>
    </Card>
  );
}



const styles = StyleSheet.create({
  card: {
    marginVertical: 14,
    marginHorizontal: 16,
    borderRadius: 18,
    overflow: 'visible',
    elevation: 4,
    backgroundColor: 'transparent',
    shadowColor: '#1976d2',
    shadowOpacity: 0.08,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    borderWidth: 0,
  },
  cardBg: {
    backgroundColor: '#fff',
    borderRadius: 18,
    padding: 16,
    minHeight: 120,
    flex: 1,
  },
  infoArea: {
    flex: 1,
    flexDirection: 'column',
    marginLeft: 10,
    minHeight: 110,
    justifyContent: 'flex-start',
  },
  coverShadow: {
    shadowColor: '#1976d2',
    shadowOpacity: 0.10,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    borderRadius: 10,
    marginRight: 10,
    backgroundColor: '#fff',
    elevation: 2,
    borderWidth: 0.5,
    borderColor: '#e3f0fc',
  },
  cover: {
    width: 74,
    height: 110,
    borderRadius: 10,
    borderWidth: 0,
  },
  title: {
    fontWeight: 'bold',
    marginBottom: 6,
    color: '#232526',
    fontSize: 19,
    letterSpacing: 0.2,
  },
  authors: {
    color: '#607d8b',
    fontWeight: '500',
    fontSize: 14,
    marginBottom: 4,
  },
  description: {
    marginBottom: 10,
    color: '#37474f',
    fontSize: 13,
    opacity: 0.92,
  },
  categories: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
    marginBottom: 6,
    marginTop: 2,
  },
  chip: {
    marginRight: 4,
    marginBottom: 2,
    borderRadius: 8,
    backgroundColor: '#e3f0fc',
    elevation: 0,
    borderWidth: 0,
  },
  footerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    gap: 10,
  },
  footerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 8,
    opacity: 0.85,
  },
  date: {
    color: '#1976d2',
    fontWeight: 'bold',
    marginLeft: 2,
  },
  pages: {
    color: '#607d8b',
    fontWeight: 'bold',
    marginLeft: 2,
  },
  actionButtonArea: {
    marginLeft: 12,
    marginRight: 2,
    marginTop: 2,
    alignSelf: 'flex-start',
    backgroundColor: 'transparent',
  },
  iconButton: {
    backgroundColor: 'transparent',
    borderRadius: 16,
    padding: 4,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 0,
    borderWidth: 0,
    shadowColor: 'transparent',
  },
});
