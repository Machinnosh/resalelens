import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { formatPrice } from '@/lib/formatting';

interface Props {
  newPrice: number;
  resalePrice1Year: number;
  resalePrice3Year: number;
}

export function ActualCostCard({ newPrice, resalePrice1Year, resalePrice3Year }: Props) {
  const [period, setPeriod] = useState<'1year' | '3year'>('1year');
  const resalePrice = period === '1year' ? resalePrice1Year : resalePrice3Year;
  const months = period === '1year' ? 12 : 36;
  const actualCost = newPrice - resalePrice;
  const monthlyCost = Math.round(actualCost / months);
  const isProfit = actualCost < 0;

  return (
    <View style={styles.card}>
      <Text style={styles.title}>実質保有コスト</Text>

      <View style={styles.toggleRow}>
        <TouchableOpacity
          style={[styles.toggleBtn, period === '1year' && styles.toggleActive]}
          onPress={() => setPeriod('1year')}
        >
          <Text style={[styles.toggleText, period === '1year' && styles.toggleTextActive]}>1年後</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.toggleBtn, period === '3year' && styles.toggleActive]}
          onPress={() => setPeriod('3year')}
        >
          <Text style={[styles.toggleText, period === '3year' && styles.toggleTextActive]}>3年後</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>新品定価</Text>
        <Text style={styles.value}>{formatPrice(newPrice)}</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>予想リセール価格</Text>
        <Text style={styles.value}>{formatPrice(resalePrice)}</Text>
      </View>
      <View style={[styles.row, styles.divider]}>
        <Text style={styles.label}>実質コスト</Text>
        <Text style={[styles.value, isProfit ? styles.profit : styles.cost]}>
          {isProfit ? '+' : ''}{formatPrice(Math.abs(actualCost))}
        </Text>
      </View>

      <View style={styles.highlight}>
        <Text style={styles.highlightLabel}>月あたり</Text>
        <Text style={[styles.highlightValue, isProfit ? styles.profit : styles.cost]}>
          {isProfit ? '利益 ' : ''}{formatPrice(Math.abs(monthlyCost))}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: '#F9FAFB', borderRadius: 16, padding: 20, gap: 12, width: '100%' },
  title: { fontSize: 16, fontWeight: '700', color: '#111827' },
  toggleRow: { flexDirection: 'row', gap: 8 },
  toggleBtn: { paddingHorizontal: 16, paddingVertical: 6, borderRadius: 20, backgroundColor: '#E5E7EB' },
  toggleActive: { backgroundColor: '#1F2937' },
  toggleText: { fontSize: 13, color: '#6B7280', fontWeight: '600' },
  toggleTextActive: { color: '#FFFFFF' },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  divider: { borderTopWidth: 1, borderTopColor: '#E5E7EB', paddingTop: 12 },
  label: { fontSize: 14, color: '#6B7280' },
  value: { fontSize: 14, fontWeight: '600', color: '#111827' },
  profit: { color: '#10B981' },
  cost: { color: '#EF4444' },
  highlight: {
    backgroundColor: '#111827', borderRadius: 12, padding: 16,
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
  },
  highlightLabel: { fontSize: 14, color: '#9CA3AF', fontWeight: '600' },
  highlightValue: { fontSize: 22, fontWeight: '800', color: '#FFFFFF' },
});
