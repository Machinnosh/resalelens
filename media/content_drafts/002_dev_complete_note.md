# 【note記事ドラフト】個人開発アプリ「リセールレンズ」MVP完成。4週間で作ったブランド品リセール分析アプリの全技術スタック

## リード
「エルメスのバーキンは買った瞬間に15%値上がりする」
「コーチのバッグは1年で55%値下がりする」

この事実をデータで可視化するアプリ「リセールレンズ」のMVPが完成しました。

4週間の個人開発の全記録を公開します。

## 技術スタック

### フロントエンド
- **Expo SDK 55** + Expo Router（ファイルベースルーティング）
- **TypeScript** 全ファイル型付き
- **zustand** 状態管理（軽量でboilerplate少）
- **@tanstack/react-query** API通信＋キャッシュ
- **react-native-gifted-charts** 価格推移グラフ

### バックエンド
- **Supabase** (PostgreSQL + Edge Functions)
- 東京リージョン（ap-northeast-1）で低レイテンシ
- 6テーブル + RLS + 5つのEdge Functions

### データ収集
- **Python** + httpx + BeautifulSoup + Playwright
- 6ソース: メルカリ、ヤフオク、ラクマ、コメ兵、大黒屋、ブランディア
- Celery + Redisで毎日自動スクレイピング

### ML
- **LightGBM** で価格予測（PRR: Price Retention Ratio）
- 時系列クロスバリデーション
- MAPE 15%以下が目標

## 数字で見るMVP

| 項目 | 数値 |
|---|---|
| TypeScriptファイル | 20+ |
| Pythonファイル | 12 |
| 対応ブランド | 18 |
| 登録商品数 | 81 |
| データソース | 6 |
| Edge Functions | 5 |
| DBテーブル | 6 |
| UIコンポーネント | 8 |
| 画面数 | 6 |

## 開発で学んだこと

### 1. Expo managed workflowの威力
XcodeもAndroid Studioも不要。Windows PCだけでiOS/Androidアプリが作れる。EASクラウドビルドの無料枠（月30ビルド）で十分。

### 2. Supabase Edge Functionsは本当に便利
PostgreSQL + RESTful API + Edge Functions + Auth が1つのダッシュボードで管理できる。個人開発に最適。

### 3. ブランド品のリセールデータは宝の山
分析してみると、「高いブランドほど実質コスパが良い」という直感に反する事実がデータで裏付けられた。これはコンテンツとしても価値がある。

## 次のステップ

- ストア審査提出（App Store + Google Play）
- 実データでのML精度検証
- Phase 2: 画像認識（写真でブランド特定）

---

開発の詳細はXでも発信中 → @shawshank827

#個人開発 #Expo #ReactNative #Supabase #機械学習 #ブランド #リセール
