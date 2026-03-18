import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { LineChart } from 'react-native-gifted-charts';

interface Props {
  decayCurve: { month: number; prr: number }[];
  categoryAverage?: { month: number; prr: number }[];
}

export function DecayCurveChart({ decayCurve, categoryAverage }: Props) {
  const productData = decayCurve.map((d) => ({
    value: d.prr * 100,
    label: d.month === 0 ? '0' : d.month % 12 === 0 ? `${d.month}M` : '',
  }));

  const avgData = categoryAverage?.map((d) => ({
    value: d.prr * 100,
  }));

  return (
    <View style={styles.card}>
      <Text style={styles.title}>価格推移（PRR）</Text>
      <Text style={styles.subtitle}>購入時を100%とした価値の推移</Text>
      <View style={styles.chartWrapper}>
        <LineChart
          data={productData}
          data2={avgData}
          height={180}
          width={280}
          spacing={40}
          initialSpacing={10}
          color1="#3B82F6"
          color2="#D1D5DB"
          dataPointsColor1="#3B82F6"
          dataPointsColor2="#D1D5DB"
          dataPointsRadius1={4}
          dataPointsRadius2={3}
          thickness1={2.5}
          thickness2={1.5}
          startFillColor1="rgba(59,130,246,0.15)"
          endFillColor1="rgba(59,130,246,0.01)"
          areaChart
          yAxisTextStyle={{ fontSize: 10, color: '#9CA3AF' }}
          xAxisLabelTextStyle={{ fontSize: 10, color: '#9CA3AF' }}
          hideRules
          maxValue={130}
          noOfSections={4}
          yAxisColor="transparent"
          xAxisColor="#E5E7EB"
        />
      </View>
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: '#3B82F6' }]} />
          <Text style={styles.legendText}>この商品</Text>
        </View>
        {categoryAverage && (
          <View style={styles.legendItem}>
            <View style={[styles.legendDot, { backgroundColor: '#D1D5DB' }]} />
            <Text style={styles.legendText}>カテゴリ平均</Text>
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: '#F9FAFB', borderRadius: 16, padding: 20, gap: 8, width: '100%' },
  title: { fontSize: 16, fontWeight: '700', color: '#111827' },
  subtitle: { fontSize: 12, color: '#9CA3AF' },
  chartWrapper: { marginTop: 8, alignItems: 'center' },
  legend: { flexDirection: 'row', gap: 16, marginTop: 8 },
  legendItem: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  legendDot: { width: 10, height: 10, borderRadius: 5 },
  legendText: { fontSize: 12, color: '#6B7280' },
});
