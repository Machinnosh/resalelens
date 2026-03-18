export function formatPrice(price: number): string {
  return `¥${price.toLocaleString('ja-JP')}`;
}

export function formatPRR(prr: number): string {
  return `${(prr * 100).toFixed(1)}%`;
}

export function formatMonthlyCost(totalCost: number, months: number): string {
  if (months <= 0) return formatPrice(totalCost);
  return formatPrice(Math.round(totalCost / months));
}

export function getScoreColor(score: number): string {
  if (score <= 30) return '#EF4444';
  if (score <= 60) return '#F59E0B';
  return '#10B981';
}

export function getScoreLabel(score: number): string {
  if (score <= 30) return '低い';
  if (score <= 60) return '普通';
  return '高い';
}

export function getConfidenceLabel(confidence: string): { label: string; color: string } {
  switch (confidence) {
    case 'high':
      return { label: '信頼度: 高', color: '#10B981' };
    case 'medium':
      return { label: '信頼度: 中', color: '#F59E0B' };
    case 'low':
      return { label: '信頼度: 低', color: '#EF4444' };
    default:
      return { label: '信頼度: 不明', color: '#9CA3AF' };
  }
}

export function getTierColor(tier: number): string {
  switch (tier) {
    case 1: return '#D4AF37';
    case 2: return '#C0C0C0';
    case 3: return '#CD7F32';
    default: return '#9CA3AF';
  }
}

export function getTierLabel(tier: number): string {
  switch (tier) {
    case 1: return 'ハイエンド';
    case 2: return 'ラグジュアリー';
    case 3: return 'プレミアム';
    default: return '';
  }
}
