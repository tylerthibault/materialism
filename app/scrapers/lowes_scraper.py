"""Lowe's scraper using their public website.
Product pages embed pricing in __NEXT_DATA__ JSON — no API key needed.
"""
import requests
import logging
import json
import re

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.lowes.com/',
}


class LowesScraper:
    """Scrapes Lowe's product/price data via their website."""

    def fetch_price(self, item_name, store_name="Lowe's"):
        """Search Lowe's for an item and return the first result's price."""
        try:
            return self._scrape_search(item_name)
        except Exception as e:
            logger.warning(f"Lowe's scraper failed for '{item_name}': {e}")
            return None

    def _scrape_search(self, query):
        """Hit the Lowe's search endpoint and parse __NEXT_DATA__."""
        url = f"https://www.lowes.com/search?searchTerm={requests.utils.quote(query)}"
        resp = requests.get(url, headers=HEADERS, timeout=12)

        if resp.status_code != 200:
            logger.warning(f"Lowe's returned {resp.status_code} for: {query}")
            return None

        html = resp.text

        # __NEXT_DATA__ contains full product listing data
        next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
        if next_data_match:
            try:
                next_data = json.loads(next_data_match.group(1))
                # Navigate the data tree to find products
                props = next_data.get('props', {}).get('pageProps', {})
                # Try common paths
                products = (
                    props.get('searchResults', {}).get('products', []) or
                    props.get('products', []) or
                    props.get('searchData', {}).get('products', [])
                )
                if products:
                    first = products[0]
                    price = (
                        first.get('price', {}).get('sellingPrice') or
                        first.get('price', {}).get('regularPrice') or
                        first.get('price')
                    )
                    if price:
                        return {
                            'price_per_unit': float(price),
                            'product_name': first.get('description', query),
                            'product_url': 'https://www.lowes.com' + first.get('productUrl', ''),
                            'availability': 'in_stock',
                            'source': 'lowes_scrape',
                        }
            except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
                logger.debug(f"__NEXT_DATA__ parse failed: {e}")

        # Fallback: JSON-LD
        ld_match = re.search(r'<script type="application/ld\+json">(.+?)</script>', html, re.DOTALL)
        if ld_match:
            try:
                ld = json.loads(ld_match.group(1))
                items = ld if isinstance(ld, list) else [ld]
                for item in items:
                    offers = item.get('offers', {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    price = offers.get('price') or offers.get('lowPrice')
                    if price:
                        return {
                            'price_per_unit': float(price),
                            'product_name': item.get('name', query),
                            'product_url': url,
                            'availability': 'in_stock',
                            'source': 'lowes_scrape',
                        }
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        return None
