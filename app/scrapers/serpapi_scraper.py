"""SerpAPI scraper for Home Depot and Lowe's.
Requires SERPAPI_KEY in environment. Free tier: 100 searches/month.

- Home Depot: uses the native 'home_depot' engine
- Lowe's: uses 'google_shopping' engine filtered to lowes.com

Key improvement: _best_match() scores all returned products against the
search query and picks the closest match rather than blindly taking [0].
"""
import os
import re
import logging

import requests

logger = logging.getLogger(__name__)

SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '')
SERPAPI_BASE = 'https://serpapi.com/search'


def _tokenize(text):
    """Lower-case, split on non-alphanumeric, return set of tokens.
    Also normalises common unit variants: '80lb' -> {'80', 'lb'},  '4x8' -> {'4', '8'}.
    """
    text = text.lower()
    # split camelCase / numbers glued to letters: '80lb' -> '80 lb'
    text = re.sub(r'(\d+)([a-z])', r'\1 \2', text)
    text = re.sub(r'([a-z])(\d+)', r'\1 \2', text)
    return set(re.split(r'[^a-z0-9]+', text)) - {'', 'the', 'a', 'an', 'and', 'or', 'in', 'at'}


def _match_score(query: str, title: str) -> float:
    """Return fraction of query tokens found in title tokens (0.0 – 1.0).
    Penalises heavily if numeric tokens (weights/sizes) in the query are
    absent from the title — a 60 lb bag should NOT match an 80 lb query.
    """
    q_tokens = _tokenize(query)
    t_tokens = _tokenize(title)

    if not q_tokens:
        return 0.0

    # Numbers/units are critical — penalise missing ones hard
    q_nums = {t for t in q_tokens if re.match(r'^\d+$', t)}
    missing_nums = q_nums - t_tokens
    if missing_nums:
        # For every missing numeric token, halve the score
        penalty = 0.5 ** len(missing_nums)
    else:
        penalty = 1.0

    overlap = len(q_tokens & t_tokens) / len(q_tokens)
    return overlap * penalty


def _best_match(query: str, products: list, price_key='price', title_key='title',
                link_key='link', min_score=0.25):
    """Pick the product whose title best matches the query.
    Returns (product_dict, score) or (None, 0) if nothing meets min_score.
    """
    best, best_score = None, 0.0
    for p in products:
        title = p.get(title_key, '')
        score = _match_score(query, title)
        logger.debug(f"  score={score:.2f}  title={title!r}")
        if score > best_score:
            best_score = score
            best = p
    if best is None or best_score < min_score:
        return None, 0.0
    return best, best_score


class SerpAPIScraper:
    def __init__(self, zip_code=None):
        self.api_key = SERPAPI_KEY
        self.zip_code = zip_code

    def _available(self):
        return bool(self.api_key)

    def fetch_price(self, item_name, store_name, zip_code=None):
        if not self._available():
            return None
        effective_zip = zip_code or self.zip_code
        if store_name == 'Home Depot':
            return self._fetch_home_depot(item_name, effective_zip)
        elif store_name in ("Lowe's", 'Lowes'):
            return self._fetch_lowes(item_name, effective_zip)
        return None

    def _fetch_home_depot(self, item_name, zip_code=None):
        try:
            params = {
                'engine': 'home_depot',
                'q': item_name,
                'api_key': self.api_key,
            }
            if zip_code:
                params['delivery_zip'] = zip_code
            resp = requests.get(SERPAPI_BASE, params=params, timeout=12)
            resp.raise_for_status()
            data = resp.json()

            products = data.get('products') or data.get('products_results') or []
            if not products:
                return None

            logger.info(f"HD search '{item_name}': {len(products)} results, picking best match")
            product, score = _best_match(item_name, products,
                                         price_key='price', title_key='title', link_key='link')
            if not product:
                logger.warning(f"HD: no good match for '{item_name}' (best score too low)")
                return None

            price = self._parse_price(product.get('price', 0))
            if not price:
                return None

            logger.info(f"HD matched: {product.get('title')!r} @ ${price} (score={score:.2f})")
            return {
                'price_per_unit': price,
                'product_name': product.get('title', item_name),
                'product_url': product.get('link', ''),
                'availability': 'in_stock',
                'source': 'serpapi_hd',
                'match_score': round(score, 2),
            }
        except Exception as e:
            logger.warning(f"SerpAPI HD error for '{item_name}': {e}")
            return None

    def _fetch_lowes(self, item_name, zip_code=None):
        try:
            params = {
                'engine': 'google_shopping',
                'q': f'{item_name} lowes',
                'api_key': self.api_key,
            }
            if zip_code:
                params['location'] = zip_code
            resp = requests.get(SERPAPI_BASE, params=params, timeout=12)
            resp.raise_for_status()
            data = resp.json()

            results = data.get('shopping_results', [])
            # Prefer Lowe's-sourced results; fall back to all if none tagged
            lowes_results = [r for r in results if 'lowe' in (r.get('source') or '').lower()]
            pool = lowes_results if lowes_results else results
            if not pool:
                return None

            logger.info(f"Lowe's search '{item_name}': {len(pool)} results, picking best match")
            product, score = _best_match(item_name, pool,
                                         price_key='price', title_key='title', link_key='link')
            if not product:
                logger.warning(f"Lowe's: no good match for '{item_name}' (best score too low)")
                return None

            price = self._parse_price(product.get('price', '0'))
            if not price:
                return None

            logger.info(f"Lowe's matched: {product.get('title')!r} @ ${price} (score={score:.2f})")
            return {
                'price_per_unit': price,
                'product_name': product.get('title', item_name),
                'product_url': product.get('link', ''),
                'availability': 'in_stock',
                'source': 'serpapi_lowes',
                'match_score': round(score, 2),
            }
        except Exception as e:
            logger.warning(f"SerpAPI Lowe's error for '{item_name}': {e}")
            return None

    @staticmethod
    def _parse_price(raw_price):
        if isinstance(raw_price, (int, float)):
            return float(raw_price) if raw_price > 0 else None
        if isinstance(raw_price, str):
            cleaned = raw_price.replace('$', '').replace(',', '').strip()
            try:
                val = float(cleaned)
                return val if val > 0 else None
            except ValueError:
                return None
        return None
