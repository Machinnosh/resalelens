import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, FlatList, TouchableOpacity } from 'react-native';
import { router } from 'expo-router';
import { SearchBar } from '@/components/SearchBar';
import { BrandCard } from '@/components/BrandCard';
import { useSearch } from '@/hooks/useSearch';
import { BRANDS } from '@/constants/brands';
import { useColorScheme } from '@/components/useColorScheme';
import { getScoreColor } from '@/lib/formatting';

export default function SearchTab() {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const [query, setQuery] = useState('');
  const { results, isSearching, search } = useSearch();

  const tier1Brands = BRANDS.filter((b) => b.tier === 1);
  const tier2Brands = BRANDS.filter((b) => b.tier === 2);

  const handleQueryChange = (text: string) => {
    setQuery(text);
    search(text);
  };

  const handleBrandPress = (slug: string) => {
    router.push(`/brand/${slug}` as any);
  };

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: isDark ? '#000' : '#FAFAFA' }]}
      contentContainerStyle={styles.content}
      keyboardShouldPersistTaps="handled"
    >
      <View style={styles.hero}>
        <Text style={[styles.tagline, isDark && { color: '#FFF' }]}>
          ブランド品の{'\n'}「本当の値段」がわかる
        </Text>
        <Text style={styles.subtitle}>
          実際の取引データに基づくリセール価値分析
        </Text>
      </View>

      <SearchBar value={query} onChangeText={handleQueryChange} />

      {query.length > 0 && results.length > 0 ? (
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, isDark && { color: '#FFF' }]}>検索結果</Text>
          {results.map((item) => (
            <TouchableOpacity
              key={item.product.id}
              style={[styles.resultRow, isDark && { backgroundColor: '#1F2937' }]}
              onPress={() => router.push(`/result/${item.product.id}` as any)}
            >
              <View style={{ flex: 1 }}>
                <Text style={[styles.resultBrand, isDark && { color: '#9CA3AF' }]}>{item.brand.nameJa}</Text>
                <Text style={[styles.resultName, isDark && { color: '#FFF' }]}>{item.product.name}</Text>
              </View>
              <Text style={styles.resultType}>
                {item.product.itemType === 'bag' ? 'バッグ' : item.product.itemType === 'wallet' ? '財布' : '時計'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      ) : (
        <>
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, isDark && { color: '#FFF' }]}>Tier 1 ブランド</Text>
            <Text style={styles.sectionSub}>最高リセール価値</Text>
            <View style={styles.brandGrid}>
              {tier1Brands.map((brand) => (
                <BrandCard
                  key={brand.id}
                  nameJa={brand.nameJa}
                  name={brand.name}
                  tier={brand.tier}
                  onPress={() => handleBrandPress(brand.slug)}
                />
              ))}
            </View>
          </View>

          <View style={styles.section}>
            <Text style={[styles.sectionTitle, isDark && { color: '#FFF' }]}>Tier 2 ブランド</Text>
            <Text style={styles.sectionSub}>ラグジュアリー</Text>
            <View style={styles.brandGrid}>
              {tier2Brands.map((brand) => (
                <BrandCard
                  key={brand.id}
                  nameJa={brand.nameJa}
                  name={brand.name}
                  tier={brand.tier}
                  onPress={() => handleBrandPress(brand.slug)}
                />
              ))}
            </View>
          </View>

          <View style={[styles.infoCard, isDark && { backgroundColor: '#1F2937' }]}>
            <Text style={[styles.infoTitle, isDark && { color: '#FFF' }]}>リセールスコアとは？</Text>
            <Text style={[styles.infoText, isDark && { color: '#D1D5DB' }]}>
              実際の取引データを独自のアルゴリズムで分析し、{'\n'}
              ブランド品の「再販価値」を0〜100のスコアで表示します。{'\n'}
              スコアが高いほど、値落ちしにくいアイテムです。
            </Text>
          </View>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 20, paddingBottom: 40 },
  hero: { marginBottom: 20, gap: 8 },
  tagline: { fontSize: 26, fontWeight: '800', color: '#111827', lineHeight: 36 },
  subtitle: { fontSize: 14, color: '#6B7280' },
  section: { marginTop: 28, gap: 8 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#111827' },
  sectionSub: { fontSize: 12, color: '#9CA3AF', marginBottom: 4 },
  brandGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  resultRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    padding: 14,
    borderRadius: 12,
    marginBottom: 6,
  },
  resultBrand: { fontSize: 11, color: '#9CA3AF', fontWeight: '600' },
  resultName: { fontSize: 15, fontWeight: '600', color: '#111827' },
  resultType: { fontSize: 12, color: '#6B7280', backgroundColor: '#F3F4F6', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  infoCard: {
    marginTop: 28,
    backgroundColor: '#F0F9FF',
    borderRadius: 16,
    padding: 20,
    gap: 8,
  },
  infoTitle: { fontSize: 15, fontWeight: '700', color: '#111827' },
  infoText: { fontSize: 13, color: '#4B5563', lineHeight: 20 },
});
