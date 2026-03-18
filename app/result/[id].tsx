import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, Stack } from 'expo-router';
import { ResaleScoreGauge } from '@/components/ResaleScoreGauge';
import { ActualCostCard } from '@/components/ActualCostCard';
import { DecayCurveChart } from '@/components/DecayCurveChart';
import { ConfidenceBadge } from '@/components/ConfidenceBadge';
import { useResaleAnalysis } from '@/hooks/useResaleData';
import { BRANDS, MODELS, CATEGORY_AVERAGE_CURVES } from '@/constants/brands';
import { formatPrice } from '@/lib/formatting';
import { useColorScheme } from '@/components/useColorScheme';

export default function ResultScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const { data: analysis, isLoading } = useResaleAnalysis(id ?? '');

  // Parse product info from ID (format: brand-slug-model-slug)
  const parts = (id ?? '').split('-');
  const brandSlug = parts.slice(0, parts.length > 2 ? -1 : parts.length).join('-');

  // Find brand and model info
  let brandName = '';
  let modelName = '';
  let newPrice = 0;
  let itemType: 'bag' | 'wallet' | 'watch' = 'bag';

  for (const brand of BRANDS) {
    if (id?.startsWith(brand.slug)) {
      brandName = brand.nameJa;
      const models = MODELS[brand.slug] ?? [];
      for (const model of models) {
        if (id?.includes(model.slug)) {
          modelName = model.nameJa;
          newPrice = Math.round((model.newPriceRange[0] + model.newPriceRange[1]) / 2);
          itemType = model.itemType;
          break;
        }
      }
      break;
    }
  }

  if (isLoading || !analysis) {
    return (
      <View style={[styles.container, styles.center, { backgroundColor: isDark ? '#000' : '#FAFAFA' }]}>
        <Stack.Screen options={{ title: '分析中...', headerBackTitle: '戻る' }} />
        <Text style={{ color: isDark ? '#FFF' : '#111827' }}>データを読み込み中...</Text>
      </View>
    );
  }

  const resalePrice1Year = Math.round(newPrice * analysis.prr1Year);
  const resalePrice3Year = Math.round(newPrice * analysis.prr3Year);
  const categoryAvg = CATEGORY_AVERAGE_CURVES[itemType];

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: isDark ? '#000' : '#FAFAFA' }]}
      contentContainerStyle={styles.content}
    >
      <Stack.Screen
        options={{
          title: `${brandName} ${modelName}`,
          headerBackTitle: '戻る',
          headerStyle: { backgroundColor: isDark ? '#111827' : '#FFF' },
          headerTintColor: isDark ? '#FFF' : '#111827',
        }}
      />

      <View style={styles.productHeader}>
        <Text style={[styles.brandLabel, isDark && { color: '#9CA3AF' }]}>{brandName}</Text>
        <Text style={[styles.productName, isDark && { color: '#FFF' }]}>{modelName}</Text>
        <Text style={styles.priceLabel}>新品定価: {formatPrice(newPrice)}</Text>
      </View>

      <ResaleScoreGauge score={analysis.resaleScore} />

      <ConfidenceBadge confidence={analysis.confidence} transactionCount={analysis.transactionCount} />

      <ActualCostCard
        newPrice={newPrice}
        resalePrice1Year={resalePrice1Year}
        resalePrice3Year={resalePrice3Year}
      />

      {analysis.decayCurve.length > 0 && (
        <DecayCurveChart decayCurve={analysis.decayCurve} categoryAverage={categoryAvg} />
      )}

      <TouchableOpacity style={styles.ctaButton}>
        <Text style={styles.ctaText}>買取査定に出す</Text>
        <Text style={styles.ctaSub}>提携ショップで無料査定</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { justifyContent: 'center', alignItems: 'center' },
  content: { padding: 20, paddingBottom: 40, gap: 20, alignItems: 'center' },
  productHeader: { alignItems: 'center', gap: 4, marginBottom: 8 },
  brandLabel: { fontSize: 13, color: '#6B7280', fontWeight: '600' },
  productName: { fontSize: 24, fontWeight: '800', color: '#111827' },
  priceLabel: { fontSize: 14, color: '#9CA3AF' },
  ctaButton: {
    backgroundColor: '#111827',
    borderRadius: 14,
    padding: 18,
    width: '100%',
    alignItems: 'center',
    gap: 4,
    marginTop: 8,
  },
  ctaText: { fontSize: 16, fontWeight: '700', color: '#FFFFFF' },
  ctaSub: { fontSize: 12, color: '#9CA3AF' },
});
