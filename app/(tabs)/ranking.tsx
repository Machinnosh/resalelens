import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';
import { router } from 'expo-router';
import { BrandTierRanking } from '@/components/BrandTierRanking';
import { useRanking } from '@/hooks/useResaleData';
import { useAppStore } from '@/stores/useAppStore';
import { useColorScheme } from '@/components/useColorScheme';
import { getTierLabel } from '@/lib/formatting';

export default function RankingTab() {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const { selectedTier, setTier } = useAppStore();
  const { data: rankings, isLoading, refetch } = useRanking(selectedTier);

  const tiers: (1 | 2 | 3)[] = [1, 2, 3];

  return (
    <View style={[styles.container, { backgroundColor: isDark ? '#000' : '#FAFAFA' }]}>
      <View style={styles.tierRow}>
        {tiers.map((tier) => (
          <TouchableOpacity
            key={tier}
            style={[
              styles.tierPill,
              selectedTier === tier && styles.tierPillActive,
              isDark && selectedTier !== tier && { backgroundColor: '#1F2937' },
            ]}
            onPress={() => setTier(tier)}
          >
            <Text
              style={[
                styles.tierText,
                selectedTier === tier && styles.tierTextActive,
                isDark && selectedTier !== tier && { color: '#D1D5DB' },
              ]}
            >
              Tier {tier} — {getTierLabel(tier)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {isLoading ? (
        <ActivityIndicator style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={rankings}
          keyExtractor={(item) => item.product.id}
          renderItem={({ item, index }) => (
            <BrandTierRanking
              rank={index + 1}
              brandName={item.brand.nameJa}
              modelName={item.product.name}
              score={item.prediction.resaleScore}
              prr={item.prediction.prr1Year}
              onPress={() => router.push(`/result/${item.product.id}` as any)}
            />
          )}
          contentContainerStyle={styles.list}
          onRefresh={refetch}
          refreshing={isLoading}
          ListEmptyComponent={
            <Text style={[styles.empty, isDark && { color: '#9CA3AF' }]}>データがありません</Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  tierRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
  },
  tierPill: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#E5E7EB',
    alignItems: 'center',
  },
  tierPillActive: { backgroundColor: '#111827' },
  tierText: { fontSize: 12, fontWeight: '600', color: '#6B7280' },
  tierTextActive: { color: '#FFFFFF' },
  list: { padding: 16 },
  empty: { textAlign: 'center', marginTop: 40, color: '#6B7280' },
});
