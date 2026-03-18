import { supabase } from './supabase';
import { Brand, Product, ResalePrediction, RankingItem, SearchResult } from '@/types';
import { BRANDS, MODELS, MOCK_PREDICTIONS } from '@/constants/brands';

const API_URL = process.env.EXPO_PUBLIC_API_URL || '';

// ---- Edge Function caller with mock fallback ----

async function callEdgeFunction<T>(name: string, params?: Record<string, string>): Promise<T | null> {
  if (!API_URL) return null;
  try {
    const url = new URL(`${API_URL}/${name}`);
    if (params) {
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    }
    const res = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? ''}`,
        'Content-Type': 'application/json',
      },
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

// ---- Mock data helpers ----

function getMockRankingItems(tier: 1 | 2 | 3): RankingItem[] {
  const tierBrands = BRANDS.filter((b) => b.tier === tier);
  const items: RankingItem[] = [];

  for (const brand of tierBrands) {
    const models = MODELS[brand.slug] ?? [];
    for (const model of models.slice(0, 2)) {
      const mockKey = `${brand.slug}-${model.slug}-${model.sizes[0] ?? ''}`.replace(/-+$/, '');
      const mock = MOCK_PREDICTIONS[mockKey];
      const newPrice = Math.round((model.newPriceRange[0] + model.newPriceRange[1]) / 2);
      items.push({
        product: {
          id: `${brand.slug}-${model.slug}`,
          brandId: brand.id,
          name: `${brand.nameJa} ${model.nameJa}`,
          itemType: model.itemType,
          model: model.slug,
          size: model.sizes[0],
          newPrice,
          isClassicModel: model.isClassic,
        },
        brand,
        prediction: {
          id: `pred-${brand.slug}-${model.slug}`,
          productId: `${brand.slug}-${model.slug}`,
          resaleScore: mock?.resaleScore ?? Math.floor(40 + Math.random() * 50),
          prr6Month: mock?.prr1Year ? mock.prr1Year + 0.05 : 0.75 + Math.random() * 0.25,
          prr1Year: mock?.prr1Year ?? 0.65 + Math.random() * 0.3,
          prr3Year: mock?.prr3Year ?? 0.45 + Math.random() * 0.4,
          lambdaValue: 0.02 + Math.random() * 0.08,
          actualCost1Year: mock?.actualCost1Year ?? Math.round(newPrice * (1 - (mock?.prr1Year ?? 0.7))),
          tierRank: 0,
          tierTotal: 0,
          decayCurve: mock?.decayCurve ?? [],
          confidence: mock?.confidence ?? 'medium',
          transactionCount: mock?.transactionCount ?? Math.floor(10 + Math.random() * 100),
          modelVersion: 'mock-v1',
        },
      });
    }
  }

  items.sort((a, b) => b.prediction.resaleScore - a.prediction.resaleScore);
  items.forEach((item, i) => {
    item.prediction.tierRank = i + 1;
    item.prediction.tierTotal = items.length;
  });

  return items;
}

// ---- API Functions (Edge Function -> mock fallback) ----

export async function searchProducts(query: string): Promise<SearchResult[]> {
  // Try Edge Function first
  const remote = await callEdgeFunction<SearchResult[]>('search', { q: query });
  if (remote && remote.length > 0) return remote;

  // Fallback to local mock search
  const q = query.toLowerCase();
  const results: SearchResult[] = [];

  for (const brand of BRANDS) {
    if (brand.nameJa.includes(query) || brand.name.toLowerCase().includes(q)) {
      const models = MODELS[brand.slug] ?? [];
      for (const model of models) {
        const newPrice = Math.round((model.newPriceRange[0] + model.newPriceRange[1]) / 2);
        results.push({
          product: {
            id: `${brand.slug}-${model.slug}`,
            brandId: brand.id,
            name: `${brand.nameJa} ${model.nameJa}`,
            itemType: model.itemType,
            model: model.slug,
            size: model.sizes[0],
            newPrice,
            isClassicModel: model.isClassic,
          },
          brand,
        });
      }
    }
  }

  if (results.length === 0) {
    for (const brand of BRANDS) {
      const models = MODELS[brand.slug] ?? [];
      for (const model of models) {
        if (model.nameJa.includes(query) || model.name.toLowerCase().includes(q)) {
          const newPrice = Math.round((model.newPriceRange[0] + model.newPriceRange[1]) / 2);
          results.push({
            product: {
              id: `${brand.slug}-${model.slug}`,
              brandId: brand.id,
              name: `${brand.nameJa} ${model.nameJa}`,
              itemType: model.itemType,
              model: model.slug,
              newPrice,
              isClassicModel: model.isClassic,
            },
            brand,
          });
        }
      }
    }
  }

  return results;
}

export async function getBrands(): Promise<Brand[]> {
  const remote = await callEdgeFunction<any[]>('brands');
  if (remote && remote.length > 0) {
    return remote.map((b) => ({
      id: b.id,
      name: b.name,
      nameJa: b.name_ja,
      tier: b.tier,
      slug: b.slug,
      logoUrl: b.logo_url,
    }));
  }
  return BRANDS;
}

export async function getBrandModels(brandSlug: string) {
  return MODELS[brandSlug] ?? [];
}

export async function getResaleAnalysis(productId: string) {
  // Try Edge Function
  const remote = await callEdgeFunction<any>('resale-analysis', { product_id: productId });
  if (remote?.prediction) return remote.prediction;

  // Fallback to mock
  for (const [key, pred] of Object.entries(MOCK_PREDICTIONS)) {
    if (productId.includes(key.split('-').slice(0, 2).join('-'))) {
      return pred;
    }
  }
  return {
    resaleScore: Math.floor(40 + Math.random() * 50),
    prr1Year: 0.55 + Math.random() * 0.4,
    prr3Year: 0.35 + Math.random() * 0.45,
    actualCost1Year: Math.floor(30_000 + Math.random() * 200_000),
    confidence: 'medium' as const,
    transactionCount: Math.floor(5 + Math.random() * 80),
    decayCurve: [
      { month: 0, prr: 1.0 }, { month: 6, prr: 0.80 },
      { month: 12, prr: 0.68 }, { month: 24, prr: 0.55 }, { month: 36, prr: 0.45 },
    ],
  };
}

export async function getRanking(tier: 1 | 2 | 3): Promise<RankingItem[]> {
  const remote = await callEdgeFunction<RankingItem[]>('ranking', { tier: String(tier) });
  if (remote && remote.length > 0) return remote;
  return getMockRankingItems(tier);
}

export async function logScan(productId: string, scanType: string = 'text'): Promise<void> {
  try {
    if (API_URL) {
      await fetch(`${API_URL}/scan-log`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, scan_type: scanType }),
      });
    }
  } catch {
    // Silently fail - scan logging is non-critical
  }
}
