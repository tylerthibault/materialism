"""SerpAPI scraper for Home Depot and Lowe's."""
import os
import requests
import logging

logger = logging.getLogger(__name__)

SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '')
SERPAPI_BASE = 'https://serpapi.com/search'


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
            products = (data.get('products') or data.get('products_results') or [])
            if not products:
                return None
            first = products[0]
            raw_price = first.get('price', 0)
            price = self._parse_price(raw_price)
            if not price:
                return None
            return {
                'price_per_unit': price,
                'product_name': first.get('title', item_name),
                'product_url': first.get('link', ''),
                'availability': 'in_stock',
                'source': 'serpapi_hd',
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
            lowes_results = [r for r in results if "lowe" in (r.get('source') or '').lower()]
            if not lowes_results:
                lowes_results = results
            if not lowes_results:
                return None
            first = lowes_results[0]
            raw_price = first.get('price', '0')
            price = self._parse_price(raw_price)
            if not price:
                return None
            return {
                'price_per_unit': price,
                'product_name': first.get('title', item_name),
                'product_url': first.get('link', ''),
                'availability': 'in_stock',
                'source': 'serpapi_lowes',
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
