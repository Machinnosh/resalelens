import { create } from 'zustand';

interface AppState {
  selectedTier: 1 | 2 | 3;
  searchQuery: string;
  recentSearches: string[];
  setTier: (tier: 1 | 2 | 3) => void;
  setSearchQuery: (query: string) => void;
  addRecentSearch: (query: string) => void;
  clearRecentSearches: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedTier: 1,
  searchQuery: '',
  recentSearches: [],
  setTier: (tier) => set({ selectedTier: tier }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  addRecentSearch: (query) =>
    set((state) => ({
      recentSearches: [query, ...state.recentSearches.filter((s) => s !== query)].slice(0, 10),
    })),
  clearRecentSearches: () => set({ recentSearches: [] }),
}));
