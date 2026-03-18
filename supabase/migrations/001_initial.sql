-- ResaleLens Initial Schema
-- MVP: Luxury bags, wallets, watches

-- ブランドマスタ
CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    name_ja VARCHAR(200) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    tier INTEGER NOT NULL DEFAULT 2 CHECK (tier BETWEEN 1 AND 3),
    logo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 商品マスタ
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id),
    name VARCHAR(500) NOT NULL,
    item_type VARCHAR(50) NOT NULL CHECK (item_type IN ('bag', 'wallet', 'watch')),
    model VARCHAR(200),
    size VARCHAR(100),
    material VARCHAR(100),
    new_price INTEGER,
    release_year INTEGER,
    is_classic_model BOOLEAN DEFAULT FALSE,
    jan_code VARCHAR(13),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- リセール取引データ
CREATE TABLE resale_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    source VARCHAR(50) NOT NULL,
    sold_price INTEGER NOT NULL,
    condition VARCHAR(50),
    sold_date DATE NOT NULL,
    listing_url TEXT,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 新品価格データ
CREATE TABLE new_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    source VARCHAR(50) NOT NULL,
    price INTEGER NOT NULL,
    url TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

-- ML予測結果
CREATE TABLE resale_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    resale_score INTEGER CHECK (resale_score BETWEEN 0 AND 100),
    prr_6month FLOAT,
    prr_1year FLOAT,
    prr_3year FLOAT,
    lambda_value FLOAT,
    actual_cost_1year INTEGER,
    tier_rank INTEGER,
    tier_total INTEGER,
    decay_curve JSONB,
    confidence VARCHAR(20),
    model_version VARCHAR(50),
    transaction_count INTEGER,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id)
);

-- スキャンログ
CREATE TABLE scan_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    scan_type VARCHAR(20) DEFAULT 'text',
    device_id VARCHAR(200),
    scanned_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_products_brand ON products(brand_id);
CREATE INDEX idx_products_item_type ON products(item_type);
CREATE INDEX idx_products_model ON products(model);
CREATE INDEX idx_transactions_product_date ON resale_transactions(product_id, sold_date DESC);
CREATE INDEX idx_transactions_source ON resale_transactions(source, sold_date DESC);
CREATE INDEX idx_predictions_product ON resale_predictions(product_id);
CREATE INDEX idx_predictions_score ON resale_predictions(resale_score DESC);
CREATE INDEX idx_scan_logs_product ON scan_logs(product_id, scanned_at DESC);

-- RLS (Row Level Security)
ALTER TABLE brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE resale_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE scan_logs ENABLE ROW LEVEL SECURITY;

-- Public read access for brands, products, predictions
CREATE POLICY "Public read brands" ON brands FOR SELECT USING (true);
CREATE POLICY "Public read products" ON products FOR SELECT USING (true);
CREATE POLICY "Public read predictions" ON resale_predictions FOR SELECT USING (true);

-- Anyone can insert scan logs (anonymous tracking)
CREATE POLICY "Public insert scan_logs" ON scan_logs FOR INSERT WITH CHECK (true);
