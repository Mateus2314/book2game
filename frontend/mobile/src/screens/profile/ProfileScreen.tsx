import React from 'react';
import {ScrollView, StyleSheet, View} from 'react-native';
import {Surface, List, Button, Card, Text, Avatar} from 'react-native-paper';
import {useQuery} from '@tanstack/react-query';
import {usersApi} from '../../services/api/endpoints';
import {useAuthStore} from '../../stores/authStore';
import {authStorage} from '../../services/auth/authStorage';
import type {ProfileStackScreenProps} from '../../types/navigation';

const RecommendationIcon = (props: any) => (
  <List.Icon {...props} icon="book-arrow-right" />
);

export function ProfileScreen({
  navigation,
}: ProfileStackScreenProps<'ProfileScreen'>) {
  const logout = useAuthStore(state => state.logout);
  const user = useAuthStore(state => state.user);

  const {data: recommendations = []} = useQuery({
    queryKey: ['myRecommendations'],
    queryFn: () => usersApi.getMyRecommendations(),
  });

  const handleLogout = async () => {
    await authStorage.clearTokens();
    logout();
  };

  return (
    <Surface style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Card style={styles.card} mode="elevated">
          <Card.Content style={styles.profileHeader}>
            <Avatar.Icon size={64} icon="account" />
            <View style={styles.profileInfo}>
              <Text variant="titleLarge" style={styles.name}>
                {user?.full_name}
              </Text>
              <Text variant="bodyMedium" style={styles.email}>
                {user?.email}
              </Text>
            </View>
            <Button
              mode="outlined"
              icon="pencil"
              onPress={() => navigation.navigate('EditProfile')}
              compact>
              Editar
            </Button>
          </Card.Content>
        </Card>

        <Card style={styles.card} mode="elevated">
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Estatísticas
            </Text>
            <View style={styles.stats}>
              <View style={styles.statItem}>
                <Text variant="displaySmall" style={styles.statValue}>
                  {recommendations.length}
                </Text>
                <Text variant="bodySmall" style={styles.statLabel}>
                  Recomendações
                </Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card} mode="elevated">
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Histórico de Recomendações
            </Text>
            {recommendations.length === 0 ? (
              <Text variant="bodyMedium" style={styles.emptyText}>
                Nenhuma recomendação ainda
              </Text>
            ) : (
              recommendations
                .slice(0, 5)
                .map((rec: any) => (
                  <List.Item
                    key={rec.id}
                    title={rec.book?.title || 'Livro desconhecido'}
                    description={`${rec.games.length} jogos recomendados`}
                    left={RecommendationIcon}
                  />
                ))
            )}
          </Card.Content>
        </Card>

        <Button
          mode="contained"
          icon="logout"
          onPress={handleLogout}
          style={styles.logoutButton}
          buttonColor="#B3261E">
          Sair
        </Button>
      </ScrollView>
    </Surface>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  card: {
    marginBottom: 16,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  profileInfo: {
    flex: 1,
  },
  name: {
    fontWeight: 'bold',
  },
  email: {
    color: '#49454F',
  },
  sectionTitle: {
    fontWeight: 'bold',
    marginBottom: 16,
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    color: '#6750A4',
    fontWeight: 'bold',
  },
  statLabel: {
    color: '#79747E',
    marginTop: 4,
  },
  emptyText: {
    color: '#79747E',
    textAlign: 'center',
    paddingVertical: 16,
  },
  logoutButton: {
    marginTop: 16,
    paddingVertical: 8,
  },
});
