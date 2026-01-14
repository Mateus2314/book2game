import React from 'react';
import {StyleSheet} from 'react-native';
import {Chip} from 'react-native-paper';
import type {ReadingStatus, PlayStatus} from '../../types/api';

interface StatusChipProps {
  status: ReadingStatus | PlayStatus;
}

const statusConfig: Record<
  ReadingStatus | PlayStatus,
  {label: string; color: string}
> = {
  // Book statuses
  to_read: {label: 'Quero Ler', color: '#2196F3'},
  reading: {label: 'Lendo', color: '#FF9800'},
  finished: {label: 'Finalizado', color: '#4CAF50'},
  // Game statuses
  to_play: {label: 'Quero Jogar', color: '#9C27B0'},
  playing: {label: 'Jogando', color: '#FFC107'},
  completed: {label: 'Completado', color: '#009688'},
};

export function StatusChip({status}: StatusChipProps) {
  const config = statusConfig[status];

  return (
    <Chip
      mode="flat"
      style={{backgroundColor: config.color}}
      textStyle={styles.chipText}>
      {config.label}
    </Chip>
  );
}

const styles = StyleSheet.create({
  chipText: {
    color: '#FFFFFF',
    fontSize: 12,
  },
});
