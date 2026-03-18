# ResaleLens (リセールレンズ)

ブランド品のリセール価値を可視化するiOS/Androidアプリ。

## Tech Stack
- **Frontend**: Expo SDK 55 / Expo Router / TypeScript / React Native
- **State**: Zustand + @tanstack/react-query
- **Backend**: Supabase (PostgreSQL + Edge Functions)
- **ML**: Python + LightGBM
- **Scraping**: Python + httpx + BeautifulSoup + Playwright

## Project Structure
- `app/` - Expo Router screens (file-based routing)
- `components/` - React Native UI components
- `lib/` - Supabase client, API calls, formatting utils
- `hooks/` - React Query hooks
- `stores/` - Zustand state
- `constants/brands.ts` - Brand/model master data + mock predictions
- `scrapers/` - Python scrapers (6 sources)
- `ml/` - LightGBM training pipeline
- `tasks/` - Celery scheduled tasks
- `supabase/` - Migrations and Edge Functions
- `store-assets/` - App Store / Google Play materials

## Supabase
- Project ID: `pbnepwydakpcrlinqjgk`
- Region: ap-northeast-1 (Tokyo)
- Edge Functions: brands, search, resale-analysis, ranking, scan-log

## Key Commands
```bash
npx expo start          # Dev server
npx tsc --noEmit        # Type check
eas build --platform all --profile preview  # Test build
eas update --branch production              # OTA update
python scrapers/orchestrator.py             # Run all scrapers
```
