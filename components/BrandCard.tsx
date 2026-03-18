import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';
import { getTierColor } from '@/lib/formatting';

interface Props {
  nameJa: string;
  name: string;
  tier: number;
  onPress: () => void;
}

export function BrandCard({ nameJa, name, tier, onPress }: Props) {
  const tierColor = getTierColor(tier);

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={[styles.tierDot, { backgroundColor: tierColor }]} />
      <Text style={styles.nameJa} numberOfLines={1}>{nameJa}</Text>
      <Text style={styles.name} numberOfLines={1}>{name}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1, backgroundColor: '#FFFFFF', borderRadius: 14, padding: 16, alignItems: 'center', gap: 6,
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.06, shadowRadius: 4,
    elevation: 2, minWidth: 100,
  },
  tierDot: { width: 8, height: 8, borderRadius: 4, alignSelf: 'flex-end' },
  nameJa: { fontSize: 16, fontWeight: '700', color: '#111827', textAlign: 'center' },
  name: { fontSize: 11, color: '#9CA3AF', textAlign: 'center' },
});
