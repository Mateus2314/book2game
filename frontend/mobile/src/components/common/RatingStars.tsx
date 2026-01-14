import React from 'react';
import {View, TouchableOpacity, StyleSheet} from 'react-native';
import {Icon} from 'react-native-paper';

interface RatingStarsProps {
  rating: number;
  onRatingChange?: (rating: number) => void;
  size?: number;
  readonly?: boolean;
  color?: string;
}

export function RatingStars({
  rating,
  onRatingChange,
  size = 24,
  readonly = false,
  color = '#FFB300',
}: RatingStarsProps) {
  const handleStarPress = (index: number) => {
    if (!readonly && onRatingChange) {
      onRatingChange(index + 1);
    }
  };

  return (
    <View style={styles.container}>
      {[0, 1, 2, 3, 4].map(index => {
        const filled = index < rating;

        return readonly ? (
          <View key={index} style={styles.star}>
            <Icon
              source={filled ? 'star' : 'star-outline'}
              size={size}
              color={color}
            />
          </View>
        ) : (
          <TouchableOpacity
            key={index}
            onPress={() => handleStarPress(index)}
            style={styles.star}>
            <Icon
              source={filled ? 'star' : 'star-outline'}
              size={size}
              color={color}
            />
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  star: {
    marginRight: 4,
  },
});
