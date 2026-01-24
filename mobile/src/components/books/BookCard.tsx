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
  onPress?: () => void;
  inLibrary?: boolean;
  onLibraryChange?: (added: boolean) => void;
}

export function BookCard({book, onPress, inLibrary, onLibraryChange}: BookCardProps) {
  
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
    scale.value = withSpring(1.2, {}, () => {
      scale.value = withSpring(1);
    });
    try {
      if (inLibrary) {
        console.log('[BookCard] Removendo livro da biblioteca:', book.id);
        const resp = await usersApi.removeBookFromLibrary(book.id);
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
      <LinearGradient
        colors={["#f5f7fa", "#c3cfe2"]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.gradientBg}
      >
        <Card.Content>
          <View style={styles.row}>
            {book.image_url && (
              <Animated.View entering={FadeIn} style={styles.coverShadow}>
                <Image
                  source={{ uri: book.image_url }}
                  style={styles.cover}
                  resizeMode="cover"
                />
              </Animated.View>
            )}
            <View style={{ flex: 1, justifyContent: 'center' }}>
              {typeof book.title === 'string' || typeof book.title === 'number' ? (
                <Text variant="titleLarge" numberOfLines={2} style={styles.title}>
                  {String(book.title)}
                </Text>
              ) : null}
              {book.authors && Array.isArray(book.authors) && book.authors.length > 0 ? (
                <Text variant="bodySmall" style={styles.authors} numberOfLines={1}>
                  {book.authors.join(', ')}
                </Text>
              ) : null}
              {typeof book.description === 'string' && book.description !== '' ? (
                <Text
                  variant="bodySmall"
                  numberOfLines={3}
                  style={styles.description}>
                  {book.description}
                </Text>
              ) : null}
              {book.categories && book.categories.length > 0 && (
                <View style={styles.categories}>
                  {book.categories.slice(0, 2).map((category, index) => {
                    if (category != null && category !== '' && (typeof category === 'string' || typeof category === 'number')) {
                      return (
                        <Chip
                          key={index}
                          mode="outlined"
                          style={styles.chip}
                          textStyle={{ color: '#b0bec5', fontWeight: '600' }}
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
              <View style={styles.footer}>
                {typeof book.published_date === 'string' && book.published_date !== '' ? (
                  <View style={styles.footerItem}>
                    <MaterialCommunityIcons name="calendar" size={16} color="#90caf9" style={{marginRight: 2}} />
                    <Text variant="bodySmall" style={styles.date}>
                      {book.published_date.length === 4
                        ? book.published_date
                        : new Date(book.published_date).getFullYear()}
                    </Text>
                  </View>
                ) : null}
                {typeof book.page_count === 'number' ? (
                  <View style={styles.footerItem}>
                    <MaterialCommunityIcons name="book-open-page-variant" size={16} color="#b0bec5" style={{marginRight: 2}} />
                    <Text variant="bodySmall" style={styles.pages}>
                      {book.page_count} páginas
                    </Text>
                  </View>
                ) : null}
                <Animated.View style={[animatedStyle, styles.glowButton]}>
                  <TouchableOpacity
                    onPress={handleLibraryToggle}
                    disabled={loading}
                    accessibilityLabel={inLibrary ? 'Remover da biblioteca' : 'Adicionar à biblioteca'}
                    style={styles.iconButton}
                  >
                    <MaterialCommunityIcons
                      name={inLibrary ? 'bookmark-check' : 'bookmark-plus'}
                      size={28}
                      color={inLibrary ? '#90caf9' : '#b0bec5'}
                    />
                  </TouchableOpacity>
                </Animated.View>
              </View>
            </View>
          </View>
        </Card.Content>
      </LinearGradient>
    </Card>
  );
}



const styles = StyleSheet.create({
  card: {
    marginVertical: 14,
    marginHorizontal: 16,
    borderRadius: 18,
    overflow: 'hidden',
    elevation: 3,
    shadowColor: '#6ee2ff',
    shadowOpacity: 0.10,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    borderWidth: 2,
    borderColor: '#6ee2ff', // Neon azul gamer sutil
  },
  gradientBg: {
    borderRadius: 18,
    padding: 0,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  coverShadow: {
    shadowColor: '#6ee2ff',
    shadowOpacity: 0.18,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    borderRadius: 10,
    marginRight: 18,
    backgroundColor: '#f5f7fa',
    elevation: 2,
    borderWidth: 1.5,
    borderColor: '#6ee2ff', // Neon azul gamer sutil
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
    gap: 6,
    marginBottom: 8,
  },
  chip: {
    marginRight: 4,
    marginBottom: 4,
    borderRadius: 8,
    borderColor: '#6ee2ff',
    borderWidth: 1.2,
    backgroundColor: 'transparent',
    elevation: 0,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    gap: 14,
  },
  footerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 8,
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
  glowButton: {
    shadowColor: '#6ee2ff',
    shadowOpacity: 0.18,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 0 },
    borderRadius: 20,
    marginLeft: 8,
  },
  iconButton: {
    backgroundColor: '#e3f2fd',
    borderRadius: 20,
    padding: 6,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.2,
    borderColor: '#6ee2ff',
  },
});
