import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, Stack, router } from 'expo-router';
import { BRANDS, MODELS, ModelInfo } from '@/constants/brands';
import { formatPrice } from '@/lib/formatting';
import { useColorScheme } from '@/components/useColorScheme';

type ItemFilter = 'all' | 'bag' | 'wallet' | 'watch';

export default function BrandScreen() {
  const { brand: brandSlug } = useLocalSearchParams<{ brand: string }>();
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const [filter, setFilter] = useState<ItemFilter>('all');

  const brand = BRANDS.find((b) => b.slug === brandSlug);
  const models = MODELS[brandSlug ?? ''] ?? [];
  const filteredModels = filter === 'all' ? models : models.filter((m) => m.itemType === filter);

  const itemTypes = Array.from(new Set(models.map((m) => m.itemType)));

  const filters: { key: ItemFilter; label: string }[] = [
    { key: 'all', label: 'すべて' },
    ...(itemTypes.includes('bag') ? [{ key: 'bag' as ItemFilter, label: 'バッグ' }] : []),
    ...(itemTypes.includes('wallet') ? [{ key: 'wallet' as ItemFilter, label: '財布' }] : []),
    ...(itemTypes.includes('watch') ? [{ key: 'watch' as ItemFilter, label: '時計' }] : []),
  ];

  const handleModelPress = (model: ModelInfo) => {
    router.push(`/result/${brandSlug}-${model.slug}` as any);
  };

  return (
    <View style={[styles.container, { backgroundColor: isDark ? '#000' : '#FAFAFA' }]}>
      <Stack.Screen
        options={{
          title: brand?.nameJa ?? brandSlug ?? '',
          headerBackTitle: '戻る',
          headerStyle: { backgroundColor: isDark ? '#111827' : '#FFF' },
          headerTintColor: isDark ? '#FFF' : '#111827',
        }}
      />

      <View style={styles.filterRow}>
        {filters.map((f) => (
          <TouchableOpacity
            key={f.key}
            style={[
              styles.filterPill,
              filter === f.key && styles.filterActive,
              isDark && filter !== f.key && { backgroundColor: '#1F2937' },
            ]}
            onPress={() => setFilter(f.key)}
          >
            <Text style={[styles.filterText, filter === f.key && styles.filterTextActive]}>
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <FlatList
        data={filteredModels}
        keyExtractor={(item) => item.slug}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.modelCard, isDark && { backgroundColor: '#1F2937' }]}
            onPress={() => handleModelPress(item)}
            activeOpacity={0.7}
          >
            <View style={styles.modelInfo}>
              <Text style={[styles.modelName, isDark && { color: '#FFF' }]}>{item.nameJa}</Text>
              <Text style={styles.modelNameEn}>{item.name}</Text>
              <View style={styles.tags}>
                {item.isClassic && (
                  <View style={styles.classicTag}>
                    <Text style={styles.classicText}>定番</Text>
                  </View>
                )}
                <Text style={styles.typeTag}>
                  {item.itemType === 'bag' ? 'バッグ' : item.itemType === 'wallet' ? '財布' : '時計'}
                </Text>
              </View>
            </View>
            <View style={styles.modelMeta}>
              <Text style={styles.priceRange}>
                {formatPrice(item.newPriceRange[0])}〜
              </Text>
              <Text style={styles.sizes}>
                {item.sizes.join(' / ')}
              </Text>
            </View>
          </TouchableOpacity>
        )}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <Text style={[styles.empty, isDark && { color: '#9CA3AF' }]}>モデルが見つかりません</Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  filterRow: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
  },
  filterPill: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#E5E7EB',
  },
  filterActive: { backgroundColor: '#111827' },
  filterText: { fontSize: 13, fontWeight: '600', color: '#6B7280' },
  filterTextActive: { color: '#FFFFFF' },
  list: { padding: 16, paddingTop: 0 },
  modelCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderRadius: 14,
    padding: 16,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 3,
    elevation: 1,
  },
  modelInfo: { flex: 1, gap: 4 },
  modelName: { fontSize: 16, fontWeight: '700', color: '#111827' },
  modelNameEn: { fontSize: 12, color: '#9CA3AF' },
  tags: { flexDirection: 'row', gap: 6, marginTop: 4 },
  classicTag: {
    backgroundColor: '#FEF3C7',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  classicText: { fontSize: 11, color: '#D97706', fontWeight: '600' },
  typeTag: { fontSize: 11, color: '#6B7280' },
  modelMeta: { alignItems: 'flex-end', justifyContent: 'center', gap: 4 },
  priceRange: { fontSize: 13, fontWeight: '600', color: '#111827' },
  sizes: { fontSize: 11, color: '#9CA3AF' },
  empty: { textAlign: 'center', marginTop: 40, color: '#6B7280' },
});
