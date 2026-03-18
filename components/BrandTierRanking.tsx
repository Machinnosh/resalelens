import React from 'react';
import { TouchableOpacity, View, Text, StyleSheet } from 'react-native';
import { getScoreColor } from '@/lib/formatting';

interface Props {
  rank: number;
  brandName: string;
  modelName: string;
  score: number;
  prr: number;
  onPress?: () => void;
}

export function BrandTierRanking({ rank, brandName, modelName, score, prr, onPress }: Props) {
  const scoreColor = getScoreColor(score);
  const rankColors: Record<number, string> = { 1: '#D4AF37', 2: '#C0C0C0', 3: '#CD7F32' };
  const rankColor = rankColors[rank] ?? '#9CA3AF';

  return (
    <TouchableOpacity style={styles.row} onPress={onPress} activeOpacity={0.7}>
      <View style={[styles.rankBadge, { backgroundColor: rankColor + '20' }]}>
        <Text style={[styles.rankText, { color: rankColor }]}>{rank}</Text>
      </View>
      <View style={styles.info}>
        <Text style={styles.brand}>{brandName}</Text>
        <Text style={styles.model} numberOfLines={1}>{modelName}</Text>
      </View>
      <View style={styles.metrics}>
        <View style={[styles.scoreBadge, { backgroundColor: scoreColor + '15' }]}>
          <Text style={[styles.scoreText, { color: scoreColor }]}>{score}</Text>
        </View>
        <Text style={styles.prr}>PRR {(prr * 100).toFixed(0)}%</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row', alignItems: 'center', paddingVertical: 14, paddingHorizontal: 16,
    backgroundColor: '#FFFFFF', borderRadius: 12, gap: 12, marginBottom: 8,
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.04, shadowRadius: 3, elevation: 1,
  },
  rankBadge: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  rankText: { fontSize: 16, fontWeight: '800' },
  info: { flex: 1, gap: 2 },
  brand: { fontSize: 11, color: '#9CA3AF', fontWeight: '600' },
  model: { fontSize: 14, fontWeight: '600', color: '#111827' },
  metrics: { alignItems: 'flex-end', gap: 4 },
  scoreBadge: { paddingHorizontal: 10, paddingVertical: 3, borderRadius: 8 },
  scoreText: { fontSize: 16, fontWeight: '800' },
  prr: { fontSize: 11, color: '#6B7280' },
});
