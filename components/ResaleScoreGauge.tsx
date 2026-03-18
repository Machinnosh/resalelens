import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { getScoreColor, getScoreLabel } from '@/lib/formatting';

interface Props {
  score: number;
  size?: number;
}

export function ResaleScoreGauge({ score, size = 180 }: Props) {
  const color = getScoreColor(score);
  const label = getScoreLabel(score);
  const borderWidth = size * 0.06;

  return (
    <View style={styles.container}>
      <View
        style={[
          styles.circle,
          {
            width: size,
            height: size,
            borderRadius: size / 2,
            borderWidth,
            borderColor: color,
          },
        ]}
      >
        <Text style={[styles.score, { fontSize: size * 0.3, color }]}>{score}</Text>
        <Text style={[styles.maxScore, { fontSize: size * 0.09 }]}>/100</Text>
      </View>
      <View style={[styles.labelBadge, { backgroundColor: color + '20' }]}>
        <Text style={[styles.labelText, { color }]}>{label}</Text>
      </View>
      <Text style={styles.subtitle}>リセールスコア</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center', gap: 8 },
  circle: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'transparent',
  },
  score: { fontWeight: '800' },
  maxScore: { color: '#9CA3AF', fontWeight: '500', marginTop: -4 },
  labelBadge: {
    paddingHorizontal: 16,
    paddingVertical: 4,
    borderRadius: 12,
  },
  labelText: { fontWeight: '700', fontSize: 14 },
  subtitle: { color: '#9CA3AF', fontSize: 12 },
});
