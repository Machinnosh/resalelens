"""Product matching logic for ResaleLens.

Maps scraped item titles to known products in the database using
fuzzy string matching and brand/model keyword extraction.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Brand name aliases for normalization
BRAND_ALIASES: dict[str, list[str]] = {
    "hermes": ["エルメス", "hermes", "hermès", "HERMES"],
    "chanel": ["シャネル", "chanel", "CHANEL"],
    "louis-vuitton": ["ルイヴィトン", "ルイ・ヴィトン", "louis vuitton", "lv", "LOUIS VUITTON", "ルイビトン"],
    "rolex": ["ロレックス", "rolex", "ROLEX"],
    "omega": ["オメガ", "omega", "OMEGA"],
    "cartier": ["カルティエ", "cartier", "CARTIER"],
    "gucci": ["グッチ", "gucci", "GUCCI"],
    "prada": ["プラダ", "prada", "PRADA"],
    "celine": ["セリーヌ", "celine", "CELINE", "céline"],
    "dior": ["ディオール", "dior", "DIOR", "christian dior"],
    "bottega-veneta": ["ボッテガ", "ボッテガヴェネタ", "bottega veneta", "BOTTEGA VENETA"],
    "balenciaga": ["バレンシアガ", "balenciaga", "BALENCIAGA"],
    "saint-laurent": ["サンローラン", "saint laurent", "ysl", "イヴサンローラン"],
    "fendi": ["フェンディ", "fendi", "FENDI"],
    "coach": ["コーチ", "coach", "COACH"],
    "michael-kors": ["マイケルコース", "michael kors", "MK", "MICHAEL KORS"],
    "kate-spade": ["ケイトスペード", "kate spade", "KATE SPADE"],
    "furla": ["フルラ", "furla", "FURLA"],
}

# Model name aliases
MODEL_ALIASES: dict[str, list[str]] = {
    "birkin": ["バーキン", "birkin"],
    "kelly": ["ケリー", "kelly"],
    "picotin": ["ピコタン", "picotin"],
    "constance": ["コンスタンス", "constance"],
    "garden-party": ["ガーデンパーティ", "garden party"],
    "classic-flap": ["クラシックフラップ", "classic flap", "マトラッセ チェーン", "ダブルフラップ"],
    "boy-chanel": ["ボーイシャネル", "boy chanel", "ボーイ"],
    "deauville": ["ドーヴィル", "deauville"],
    "neverfull": ["ネヴァーフル", "ネバーフル", "neverfull"],
    "speedy": ["スピーディ", "speedy"],
    "alma": ["アルマ", "alma"],
    "capucines": ["カプシーヌ", "capucines"],
    "submariner": ["サブマリーナ", "submariner"],
    "daytona": ["デイトナ", "daytona", "コスモグラフ"],
    "datejust": ["デイトジャスト", "datejust"],
    "gmt-master-ii": ["gmt", "gmtマスター", "gmt-master"],
    "explorer": ["エクスプローラー", "explorer"],
    "speedmaster": ["スピードマスター", "speedmaster", "ムーンウォッチ"],
    "seamaster-300": ["シーマスター", "seamaster"],
    "tank": ["タンク", "tank"],
    "santos": ["サントス", "santos"],
    "ballon-bleu": ["バロンブルー", "ballon bleu"],
    "gg-marmont": ["ggマーモント", "マーモント", "marmont"],
    "galleria": ["ガレリア", "galleria", "サフィアーノ"],
    "luggage": ["ラゲージ", "luggage"],
    "lady-dior": ["レディディオール", "lady dior"],
    "book-tote": ["ブックトート", "book tote"],
}

# Size extraction patterns
SIZE_PATTERNS = [
    r"(\d{2})\s*(?:cm|mm|サイズ)",  # 25cm, 30mm
    r"サイズ\s*(\d{2})",
    r"\b(25|28|30|32|35|36|40|41|42)\b",  # Common sizes
    r"(PM|MM|GM|BB|ナノ|ミニ|スモール|ミディアム|ラージ|ジャンボ|マキシ)",
]

# Condition mapping
CONDITION_MAP = {
    "新品": "new",
    "未使用": "new",
    "美品": "excellent",
    "良品": "good",
    "やや傷あり": "fair",
    "傷あり": "poor",
    "S": "excellent",
    "A": "good",
    "B": "fair",
    "C": "poor",
    "SA": "excellent",
    "AB": "good",
}


@dataclass
class MatchResult:
    """Result of product matching."""
    brand_slug: str
    model_slug: str
    size: Optional[str]
    condition: Optional[str]
    confidence: float  # 0.0 - 1.0


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    text = text.lower()
    text = re.sub(r"[\s\u3000]+", " ", text)  # Normalize whitespace
    text = re.sub(r"[【】\[\]()（）「」『』]", " ", text)  # Remove brackets
    return text.strip()


def identify_brand(text: str) -> Optional[str]:
    """Identify brand from text."""
    normalized = normalize_text(text)
    for slug, aliases in BRAND_ALIASES.items():
        for alias in aliases:
            if alias.lower() in normalized:
                return slug
    return None


def identify_model(text: str) -> Optional[str]:
    """Identify model from text."""
    normalized = normalize_text(text)
    for slug, aliases in MODEL_ALIASES.items():
        for alias in aliases:
            if alias.lower() in normalized:
                return slug
    return None


def extract_size(text: str) -> Optional[str]:
    """Extract size from text."""
    normalized = normalize_text(text)
    for pattern in SIZE_PATTERNS:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_condition(text: str) -> Optional[str]:
    """Extract condition from text."""
    for jp_cond, en_cond in CONDITION_MAP.items():
        if jp_cond in text:
            return en_cond
    return None


def match_product(title: str, brand_hint: Optional[str] = None) -> Optional[MatchResult]:
    """
    Match a scraped item title to a known product.

    Args:
        title: The listing title to match
        brand_hint: Optional brand hint from search context

    Returns:
        MatchResult if a match is found, None otherwise
    """
    brand_slug = identify_brand(title) or brand_hint
    if not brand_slug:
        return None

    model_slug = identify_model(title)
    if not model_slug:
        return None

    size = extract_size(title)
    condition = extract_condition(title)

    # Calculate confidence based on what we matched
    confidence = 0.5  # Base confidence for brand + model match
    if size:
        confidence += 0.2
    if condition:
        confidence += 0.1
    # Boost if brand was identified from title (not just hint)
    if identify_brand(title):
        confidence += 0.2

    return MatchResult(
        brand_slug=brand_slug,
        model_slug=model_slug,
        size=size,
        condition=condition,
        confidence=min(confidence, 1.0),
    )
