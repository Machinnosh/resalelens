import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking } from 'react-native';
import { useColorScheme } from '@/components/useColorScheme';

function SettingsRow({ label, value, onPress }: { label: string; value?: string; onPress?: () => void }) {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  return (
    <TouchableOpacity
      style={[styles.row, isDark && { backgroundColor: '#1F2937' }]}
      onPress={onPress}
      disabled={!onPress}
    >
      <Text style={[styles.rowLabel, isDark && { color: '#FFF' }]}>{label}</Text>
      {value && <Text style={styles.rowValue}>{value}</Text>}
      {onPress && <Text style={styles.rowArrow}>›</Text>}
    </TouchableOpacity>
  );
}

export default function ProfileTab() {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const bg = isDark ? '#000' : '#FAFAFA';

  return (
    <ScrollView style={[styles.container, { backgroundColor: bg }]} contentContainerStyle={styles.content}>
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDark && { color: '#FFF' }]}>アプリ情報</Text>
        <SettingsRow label="バージョン" value="1.0.0" />
        <SettingsRow label="ビルド" value="MVP" />
      </View>

      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDark && { color: '#FFF' }]}>データについて</Text>
        <View style={[styles.infoBox, isDark && { backgroundColor: '#1F2937' }]}>
          <Text style={[styles.infoText, isDark && { color: '#D1D5DB' }]}>
            リセールレンズは以下のソースから取得した実際の取引データに基づいて分析しています：
          </Text>
          <Text style={[styles.infoText, isDark && { color: '#D1D5DB' }]}>
            {'\n'}• メルカリ（成約価格）{'\n'}• ヤフオク（落札価格）{'\n'}• ラクマ（成約価格）{'\n'}• コメ兵（販売価格）{'\n'}• 大黒屋（買取・販売価格）{'\n'}• ブランディア（買取価格）
          </Text>
          <Text style={[styles.infoText, isDark && { color: '#D1D5DB' }]}>
            {'\n'}データは毎日自動更新され、LightGBM機械学習モデルで価格予測を行っています。
          </Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={[styles.sectionTitle, isDark && { color: '#FFF' }]}>サポート</Text>
        <SettingsRow label="プライバシーポリシー" onPress={() => {}} />
        <SettingsRow label="利用規約" onPress={() => {}} />
        <SettingsRow label="お問い合わせ" onPress={() => Linking.openURL('mailto:atcgef@gmail.com')} />
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>ResaleLens by プライシングラボ</Text>
        <Text style={styles.footerText}>© 2026 Pricing Lab</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 20, paddingBottom: 40 },
  section: { marginBottom: 28, gap: 8 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#111827', marginBottom: 4 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 4,
  },
  rowLabel: { flex: 1, fontSize: 15, color: '#111827' },
  rowValue: { fontSize: 14, color: '#9CA3AF' },
  rowArrow: { fontSize: 20, color: '#9CA3AF', marginLeft: 8 },
  infoBox: { backgroundColor: '#FFF', borderRadius: 12, padding: 16 },
  infoText: { fontSize: 13, color: '#4B5563', lineHeight: 20 },
  footer: { alignItems: 'center', marginTop: 20, gap: 4 },
  footerText: { fontSize: 12, color: '#9CA3AF' },
});
