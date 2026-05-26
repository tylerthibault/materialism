"""Home Depot scraper using their public GraphQL endpoint.
No API key required — uses the same endpoint as their website.
Falls back gracefully if blocked.
"""
import requests
import logging
import json
import re

logger = logging.getLogger(__name__)

HD_SEARCH_URL = 'https://www.homedepot.com/federation-gateway/graphql'
HD_SEARCH_PAGE = 'https://www.homedepot.com/s/{query}'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.homedepot.com/',
}


class HomeDepotScraper:
    """Scrapes Home Depot product/price data via their website."""

    def fetch_price(self, item_name, store_name='Home Depot'):
        """Search Home Depot for an item and return the first result's price."""
        try:
            return self._scrape_search_page(item_name)
        except Exception as e:
            logger.warning(f"HomeDepot scraper failed for '{item_name}': {e}")
            return None

    def _scrape_search_page(self, query):
        """Scrape the search results page for price data in JSON-LD."""
        url = f"https://www.homedepot.com/s/{requests.utils.quote(query)}"
        resp = requests.get(url, headers=HEADERS, timeout=12)

        if resp.status_code != 200:
            logger.warning(f"Home Depot returned {resp.status_code} for query: {query}")
            return None

        # Home Depot embeds product data in a __NEXT_DATA__ script tag
        # Try to find JSON-LD structured data first
        html = resp.text
        
        # Look for price in JSON-LD
        ld_match = re.search(r'<script type="application/ld\+json">(.+?)</script>', html, re.DOTALL)
        if ld_match:
            try:
                ld_data = json.loads(ld_match.group(1))
                items = ld_data if isinstance(ld_data, list) else [ld_data]
                for item in items:
                    if item.get('@type') in ('Product', 'ItemList'):
                        offers = item.get('offers', {})
                        if isinstance(offers, list):
                            offers = offers[0] if offers else {}
                        price = offers.get('price') or offers.get('lowPrice')
                        if price:
                            return {
                                'price_per_unit': float(price),
                                'product_name': item.get('name', query),
                                'product_url': item.get('url', url),
                                'availability': 'in_stock',
                                'source': 'homedepot_scrape',
                            }
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        # Fallback: look for price patterns in HTML
        price_match = re.search(r'\$([\d,]+\.\d{2})', html)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            # Find a product title near the price
            title_match = re.search(r'<h2[^>]*class="[^"]*product[^"]*"[^>]*>([^<]+)</h2>', html, re.IGNORECASE)
            product_name = title_match.group(1).strip() if title_match else query
            return {
                'price_per_unit': float(price_str),
                'product_name': product_name,
                'product_url': url,
                'availability': 'unknown',
                'source': 'homedepot_scrape',
            }

        return None
