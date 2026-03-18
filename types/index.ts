export interface Brand {
  id: string;
  name: string;
  nameJa: string;
  tier: 1 | 2 | 3;
  logoUrl?: string;
  slug: string;
}

export interface Product {
  id: string;
  brandId: string;
  name: string;
  itemType: 'bag' | 'wallet' | 'watch';
  model: string;
  size?: string;
  material?: string;
  newPrice: number;
  releaseYear?: number;
  isClassicModel: boolean;
}

export interface ResaleTransaction {
  id: string;
  productId: string;
  source: 'mercari' | 'yahoo_auction' | 'rakuma' | 'komehyo' | 'daikokuya' | 'brandear';
  soldPrice: number;
  condition?: string;
  soldDate: string;
}

export interface ResalePrediction {
  id: string;
  productId: string;
  resaleScore: number;
  prr6Month: number;
  prr1Year: number;
  prr3Year: number;
  lambdaValue: number;
  actualCost1Year: number;
  tierRank: number;
  tierTotal: number;
  decayCurve: { month: number; prr: number }[];
  confidence: 'high' | 'medium' | 'low';
  transactionCount: number;
  modelVersion: string;
}

export interface ScanLog {
  id: string;
  productId: string;
  scanType: 'text' | 'barcode' | 'image';
  deviceId: string;
}

export interface RankingItem {
  product: Product;
  brand: Brand;
  prediction: ResalePrediction;
}

export interface SearchResult {
  product: Product;
  brand: Brand;
  prediction?: ResalePrediction;
}
