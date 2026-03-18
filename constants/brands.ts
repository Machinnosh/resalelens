import { Brand } from '@/types';

export const BRANDS: Brand[] = [
  // Tier 1
  { id: 'hermes', slug: 'hermes', name: 'Hermès', nameJa: 'エルメス', tier: 1 },
  { id: 'chanel', slug: 'chanel', name: 'CHANEL', nameJa: 'シャネル', tier: 1 },
  { id: 'louis_vuitton', slug: 'louis-vuitton', name: 'Louis Vuitton', nameJa: 'ルイ・ヴィトン', tier: 1 },
  { id: 'rolex', slug: 'rolex', name: 'Rolex', nameJa: 'ロレックス', tier: 1 },
  { id: 'omega', slug: 'omega', name: 'Omega', nameJa: 'オメガ', tier: 1 },
  { id: 'cartier', slug: 'cartier', name: 'Cartier', nameJa: 'カルティエ', tier: 1 },
  // Tier 2
  { id: 'gucci', slug: 'gucci', name: 'Gucci', nameJa: 'グッチ', tier: 2 },
  { id: 'prada', slug: 'prada', name: 'Prada', nameJa: 'プラダ', tier: 2 },
  { id: 'celine', slug: 'celine', name: 'Celine', nameJa: 'セリーヌ', tier: 2 },
  { id: 'dior', slug: 'dior', name: 'Dior', nameJa: 'ディオール', tier: 2 },
  { id: 'bottega_veneta', slug: 'bottega-veneta', name: 'Bottega Veneta', nameJa: 'ボッテガ・ヴェネタ', tier: 2 },
  { id: 'balenciaga', slug: 'balenciaga', name: 'Balenciaga', nameJa: 'バレンシアガ', tier: 2 },
  { id: 'saint_laurent', slug: 'saint-laurent', name: 'Saint Laurent', nameJa: 'サンローラン', tier: 2 },
  { id: 'fendi', slug: 'fendi', name: 'Fendi', nameJa: 'フェンディ', tier: 2 },
  // Tier 3
  { id: 'coach', slug: 'coach', name: 'Coach', nameJa: 'コーチ', tier: 3 },
  { id: 'michael_kors', slug: 'michael-kors', name: 'Michael Kors', nameJa: 'マイケル・コース', tier: 3 },
  { id: 'kate_spade', slug: 'kate-spade', name: 'Kate Spade', nameJa: 'ケイト・スペード', tier: 3 },
  { id: 'furla', slug: 'furla', name: 'Furla', nameJa: 'フルラ', tier: 3 },
];

export interface ModelInfo {
  slug: string;
  name: string;
  nameJa: string;
  itemType: 'bag' | 'wallet' | 'watch';
  sizes: string[];
  isClassic: boolean;
  newPriceRange: [number, number]; // min, max in JPY
}

export const MODELS: Record<string, ModelInfo[]> = {
  hermes: [
    { slug: 'birkin', name: 'Birkin', nameJa: 'バーキン', itemType: 'bag', sizes: ['25', '30', '35', '40'], isClassic: true, newPriceRange: [1_430_000, 2_200_000] },
    { slug: 'kelly', name: 'Kelly', nameJa: 'ケリー', itemType: 'bag', sizes: ['25', '28', '32'], isClassic: true, newPriceRange: [1_265_000, 1_870_000] },
    { slug: 'picotin', name: 'Picotin Lock', nameJa: 'ピコタン ロック', itemType: 'bag', sizes: ['18', '22'], isClassic: true, newPriceRange: [390_000, 500_000] },
    { slug: 'constance', name: 'Constance', nameJa: 'コンスタンス', itemType: 'bag', sizes: ['18', '24'], isClassic: true, newPriceRange: [1_100_000, 1_650_000] },
    { slug: 'garden-party', name: 'Garden Party', nameJa: 'ガーデンパーティ', itemType: 'bag', sizes: ['30', '36'], isClassic: false, newPriceRange: [280_000, 400_000] },
    { slug: 'bearn', name: 'Béarn', nameJa: 'ベアン', itemType: 'wallet', sizes: ['長財布', 'コンパクト'], isClassic: true, newPriceRange: [190_000, 350_000] },
    { slug: 'dogon', name: 'Dogon', nameJa: 'ドゴン', itemType: 'wallet', sizes: ['GM', 'コンパクト'], isClassic: false, newPriceRange: [200_000, 380_000] },
    { slug: 'azap', name: 'Azap', nameJa: 'アザップ', itemType: 'wallet', sizes: ['ロング', 'コンパクト'], isClassic: false, newPriceRange: [130_000, 250_000] },
  ],
  chanel: [
    { slug: 'classic-flap', name: 'Classic Flap', nameJa: 'クラシック フラップ', itemType: 'bag', sizes: ['ミニ', 'スモール', 'ミディアム', 'ジャンボ', 'マキシ'], isClassic: true, newPriceRange: [900_000, 1_650_000] },
    { slug: 'boy-chanel', name: 'Boy Chanel', nameJa: 'ボーイ シャネル', itemType: 'bag', sizes: ['スモール', 'ミディアム'], isClassic: true, newPriceRange: [750_000, 1_100_000] },
    { slug: 'matelasse', name: 'Matelassé', nameJa: 'マトラッセ', itemType: 'bag', sizes: ['スモール', 'ミディアム', 'ラージ'], isClassic: true, newPriceRange: [600_000, 1_200_000] },
    { slug: 'deauville', name: 'Deauville', nameJa: 'ドーヴィル', itemType: 'bag', sizes: ['スモール', 'ラージ'], isClassic: false, newPriceRange: [400_000, 600_000] },
    { slug: 'matelasse-long-wallet', name: 'Matelassé Long Wallet', nameJa: 'マトラッセ 長財布', itemType: 'wallet', sizes: ['ロング'], isClassic: true, newPriceRange: [150_000, 250_000] },
    { slug: 'matelasse-compact', name: 'Matelassé Compact', nameJa: 'マトラッセ コンパクト', itemType: 'wallet', sizes: ['コンパクト'], isClassic: true, newPriceRange: [100_000, 180_000] },
    { slug: 'camellia-wallet', name: 'Camellia Wallet', nameJa: 'カメリア', itemType: 'wallet', sizes: ['ロング', 'コンパクト'], isClassic: false, newPriceRange: [120_000, 200_000] },
  ],
  'louis-vuitton': [
    { slug: 'neverfull', name: 'Neverfull', nameJa: 'ネヴァーフル', itemType: 'bag', sizes: ['PM', 'MM', 'GM'], isClassic: true, newPriceRange: [230_000, 310_000] },
    { slug: 'speedy', name: 'Speedy', nameJa: 'スピーディ', itemType: 'bag', sizes: ['25', '30', '35', '40'], isClassic: true, newPriceRange: [190_000, 280_000] },
    { slug: 'alma', name: 'Alma', nameJa: 'アルマ', itemType: 'bag', sizes: ['BB', 'PM', 'MM'], isClassic: true, newPriceRange: [210_000, 350_000] },
    { slug: 'capucines', name: 'Capucines', nameJa: 'カプシーヌ', itemType: 'bag', sizes: ['BB', 'MM'], isClassic: true, newPriceRange: [550_000, 850_000] },
    { slug: 'zippy-wallet', name: 'Zippy Wallet', nameJa: 'ジッピー・ウォレット', itemType: 'wallet', sizes: ['スタンダード'], isClassic: true, newPriceRange: [100_000, 140_000] },
    { slug: 'portefeuille-sarah', name: 'Portefeuille Sarah', nameJa: 'ポルトフォイユ・サラ', itemType: 'wallet', sizes: ['スタンダード'], isClassic: true, newPriceRange: [90_000, 120_000] },
    { slug: 'portefeuille-victorine', name: 'Portefeuille Victorine', nameJa: 'ポルトフォイユ・ヴィクトリーヌ', itemType: 'wallet', sizes: ['コンパクト'], isClassic: true, newPriceRange: [75_000, 95_000] },
  ],
  rolex: [
    { slug: 'submariner', name: 'Submariner', nameJa: 'サブマリーナー', itemType: 'watch', sizes: ['41mm'], isClassic: true, newPriceRange: [1_100_000, 1_600_000] },
    { slug: 'daytona', name: 'Cosmograph Daytona', nameJa: 'デイトナ', itemType: 'watch', sizes: ['40mm'], isClassic: true, newPriceRange: [1_800_000, 5_000_000] },
    { slug: 'datejust', name: 'Datejust', nameJa: 'デイトジャスト', itemType: 'watch', sizes: ['36mm', '41mm'], isClassic: true, newPriceRange: [800_000, 1_500_000] },
    { slug: 'gmt-master-ii', name: 'GMT-Master II', nameJa: 'GMTマスター II', itemType: 'watch', sizes: ['40mm'], isClassic: true, newPriceRange: [1_200_000, 1_800_000] },
    { slug: 'explorer', name: 'Explorer', nameJa: 'エクスプローラー', itemType: 'watch', sizes: ['36mm', '40mm'], isClassic: true, newPriceRange: [900_000, 1_200_000] },
  ],
  omega: [
    { slug: 'speedmaster', name: 'Speedmaster Moonwatch', nameJa: 'スピードマスター', itemType: 'watch', sizes: ['42mm'], isClassic: true, newPriceRange: [700_000, 1_100_000] },
    { slug: 'seamaster-300', name: 'Seamaster 300M', nameJa: 'シーマスター 300M', itemType: 'watch', sizes: ['42mm'], isClassic: true, newPriceRange: [600_000, 900_000] },
    { slug: 'constellation', name: 'Constellation', nameJa: 'コンステレーション', itemType: 'watch', sizes: ['39mm', '41mm'], isClassic: true, newPriceRange: [500_000, 800_000] },
    { slug: 'aqua-terra', name: 'Seamaster Aqua Terra', nameJa: 'アクアテラ', itemType: 'watch', sizes: ['38mm', '41mm'], isClassic: false, newPriceRange: [550_000, 850_000] },
  ],
  cartier: [
    { slug: 'tank', name: 'Tank', nameJa: 'タンク', itemType: 'watch', sizes: ['スモール', 'ラージ'], isClassic: true, newPriceRange: [350_000, 1_200_000] },
    { slug: 'santos', name: 'Santos de Cartier', nameJa: 'サントス', itemType: 'watch', sizes: ['スモール', 'ミディアム', 'ラージ'], isClassic: true, newPriceRange: [600_000, 1_400_000] },
    { slug: 'ballon-bleu', name: 'Ballon Bleu', nameJa: 'バロンブルー', itemType: 'watch', sizes: ['33mm', '36mm', '42mm'], isClassic: true, newPriceRange: [500_000, 1_000_000] },
    { slug: 'panthere', name: 'Panthère', nameJa: 'パンテール', itemType: 'watch', sizes: ['スモール', 'ミディアム'], isClassic: true, newPriceRange: [450_000, 900_000] },
  ],
};

// Mock prediction data for development
export const MOCK_PREDICTIONS: Record<string, {
  resaleScore: number;
  prr1Year: number;
  prr3Year: number;
  actualCost1Year: number;
  confidence: 'high' | 'medium' | 'low';
  transactionCount: number;
  decayCurve: { month: number; prr: number }[];
}> = {
  'hermes-birkin-30': {
    resaleScore: 95,
    prr1Year: 1.15,
    prr3Year: 1.05,
    actualCost1Year: -214_500,
    confidence: 'high',
    transactionCount: 156,
    decayCurve: [
      { month: 0, prr: 1.0 }, { month: 3, prr: 1.12 }, { month: 6, prr: 1.18 },
      { month: 12, prr: 1.15 }, { month: 18, prr: 1.10 }, { month: 24, prr: 1.08 },
      { month: 30, prr: 1.06 }, { month: 36, prr: 1.05 },
    ],
  },
  'chanel-classic-flap-medium': {
    resaleScore: 88,
    prr1Year: 0.92,
    prr3Year: 0.85,
    actualCost1Year: 104_400,
    confidence: 'high',
    transactionCount: 203,
    decayCurve: [
      { month: 0, prr: 1.0 }, { month: 3, prr: 0.97 }, { month: 6, prr: 0.95 },
      { month: 12, prr: 0.92 }, { month: 18, prr: 0.89 }, { month: 24, prr: 0.87 },
      { month: 30, prr: 0.86 }, { month: 36, prr: 0.85 },
    ],
  },
  'louis-vuitton-neverfull-mm': {
    resaleScore: 72,
    prr1Year: 0.78,
    prr3Year: 0.65,
    actualCost1Year: 57_200,
    confidence: 'high',
    transactionCount: 342,
    decayCurve: [
      { month: 0, prr: 1.0 }, { month: 3, prr: 0.88 }, { month: 6, prr: 0.83 },
      { month: 12, prr: 0.78 }, { month: 18, prr: 0.73 }, { month: 24, prr: 0.69 },
      { month: 30, prr: 0.67 }, { month: 36, prr: 0.65 },
    ],
  },
  'rolex-submariner-41': {
    resaleScore: 92,
    prr1Year: 1.08,
    prr3Year: 1.02,
    actualCost1Year: -96_800,
    confidence: 'high',
    transactionCount: 189,
    decayCurve: [
      { month: 0, prr: 1.0 }, { month: 3, prr: 1.10 }, { month: 6, prr: 1.12 },
      { month: 12, prr: 1.08 }, { month: 18, prr: 1.05 }, { month: 24, prr: 1.04 },
      { month: 30, prr: 1.03 }, { month: 36, prr: 1.02 },
    ],
  },
  'coach-tabby-26': {
    resaleScore: 35,
    prr1Year: 0.45,
    prr3Year: 0.28,
    actualCost1Year: 44_000,
    confidence: 'medium',
    transactionCount: 67,
    decayCurve: [
      { month: 0, prr: 1.0 }, { month: 3, prr: 0.65 }, { month: 6, prr: 0.55 },
      { month: 12, prr: 0.45 }, { month: 18, prr: 0.38 }, { month: 24, prr: 0.33 },
      { month: 30, prr: 0.30 }, { month: 36, prr: 0.28 },
    ],
  },
};

// Category average decay curves for comparison
export const CATEGORY_AVERAGE_CURVES: Record<string, { month: number; prr: number }[]> = {
  bag: [
    { month: 0, prr: 1.0 }, { month: 3, prr: 0.82 }, { month: 6, prr: 0.75 },
    { month: 12, prr: 0.68 }, { month: 18, prr: 0.62 }, { month: 24, prr: 0.58 },
    { month: 30, prr: 0.55 }, { month: 36, prr: 0.52 },
  ],
  wallet: [
    { month: 0, prr: 1.0 }, { month: 3, prr: 0.72 }, { month: 6, prr: 0.62 },
    { month: 12, prr: 0.52 }, { month: 18, prr: 0.45 }, { month: 24, prr: 0.40 },
    { month: 30, prr: 0.37 }, { month: 36, prr: 0.35 },
  ],
  watch: [
    { month: 0, prr: 1.0 }, { month: 3, prr: 0.90 }, { month: 6, prr: 0.85 },
    { month: 12, prr: 0.80 }, { month: 18, prr: 0.77 }, { month: 24, prr: 0.74 },
    { month: 30, prr: 0.72 }, { month: 36, prr: 0.70 },
  ],
};
