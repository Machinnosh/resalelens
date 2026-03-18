import { useQuery } from '@tanstack/react-query';
import { getBrands, getBrandModels, getResaleAnalysis, getRanking } from '@/lib/api';

export function useBrands() {
  return useQuery({
    queryKey: ['brands'],
    queryFn: getBrands,
    staleTime: 1000 * 60 * 60,
  });
}

export function useBrandModels(brandSlug: string) {
  return useQuery({
    queryKey: ['brandModels', brandSlug],
    queryFn: () => getBrandModels(brandSlug),
    enabled: !!brandSlug,
    staleTime: 1000 * 60 * 60,
  });
}

export function useResaleAnalysis(productId: string) {
  return useQuery({
    queryKey: ['resaleAnalysis', productId],
    queryFn: () => getResaleAnalysis(productId),
    enabled: !!productId,
    staleTime: 1000 * 60 * 30,
  });
}

export function useRanking(tier: 1 | 2 | 3) {
  return useQuery({
    queryKey: ['ranking', tier],
    queryFn: () => getRanking(tier),
    staleTime: 1000 * 60 * 15,
  });
}
