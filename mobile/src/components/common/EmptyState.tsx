import React from 'react';
import {View, StyleSheet} from 'react-native';
import {Text, Icon} from 'react-native-paper';

interface EmptyStateProps {
  icon: string;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <View style={styles.container}>
      <Icon source={icon} size={64} color="#79747E" />
      <Text variant="titleLarge" style={styles.title}>
        {title}
      </Text>
      {description && (
        <Text variant="bodyMedium" style={styles.description}>
          {description}
        </Text>
      )}
      {action && <View style={styles.action}>{action}</View>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  title: {
    marginTop: 16,
    textAlign: 'center',
    color: '#1C1B1F',
  },
  description: {
    marginTop: 8,
    textAlign: 'center',
    color: '#49454F',
  },
  action: {
    marginTop: 24,
  },
});
