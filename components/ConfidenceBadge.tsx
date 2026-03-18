import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { getConfidenceLabel } from '@/lib/formatting';

interface Props {
  confidence: 'high' | 'medium' | 'low';
  transactionCount?: number;
}

export function ConfidenceBadge({ confidence, transactionCount }: Props) {
  const { label, color } = getConfidenceLabel(confidence);

  return (
    <View style={[styles.badge, { backgroundColor: color + '15' }]}>
      <View style={[styles.dot, { backgroundColor: color }]} />
      <Text style={[styles.text, { color }]}>{label}</Text>
      {transactionCount !== undefined && (
        <Text style={styles.count}>（{transactionCount}件の取引データ）</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, alignSelf: 'flex-start', gap: 6,
  },
  dot: { width: 8, height: 8, borderRadius: 4 },
  text: { fontSize: 13, fontWeight: '600' },
  count: { fontSize: 12, color: '#9CA3AF' },
});
