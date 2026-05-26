"""SerpAPI scraper for Home Depot and Lowe's.
Requires SERPAPI_KEY in environment. Free tier: 100 searches/month.
Docs: https://serpapi.com/home-depot-search-api
"""
import os
import requests
import logging

logger = logging.getLogger(__name__)

SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '')
SERPAPI_BASE = 'https://serpapi.com/search'


class SerpAPIScraper:
    def __init__(self):
        self.api_key = SERPAPI_KEY

    def _available(self):
        return bool(self.api_key)

    def fetch_price(self, item_name, store_name):
        if not self._available():
            return None

        engine_map = {
            'Home Depot': 'home_depot',
            'Lowes': 'lowes',
            "Lowe's": 'lowes',
        }
        engine = engine_map.get(store_name)
        if not engine:
            return None

        try:
            resp = requests.get(SERPAPI_BASE, params={
                'engine': engine,
                'q': item_name,
                'api_key': self.api_key,
            }, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # SerpAPI returns products_results for HD/Lowe's
            products = data.get('products_results') or data.get('shopping_results') or []
            if not products:
                return None

            first = products[0]
            # Extract price — SerpAPI returns it as float or string like "$4.98"
            raw_price = first.get('price', 0)
            if isinstance(raw_price, str):
                raw_price = raw_price.replace('$', '').replace(',', '').strip()
                try:
                    raw_price = float(raw_price)
                except ValueError:
                    raw_price = 0.0

            return {
                'price_per_unit': float(raw_price),
                'product_name': first.get('title', item_name),
                'product_url': first.get('link') or first.get('product_link', ''),
                'availability': 'in_stock',
                'source': 'serpapi',
            }
        except Exception as e:
            logger.warning(f"SerpAPI error for {store_name} / {item_name}: {e}")
            return None
