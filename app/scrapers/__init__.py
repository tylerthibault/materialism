"""
Scraper registry — returns a price for an item at a given store.

Priority order:
  1. SerpAPI (if SERPAPI_KEY is set)
  2. Direct website scraper (HD / Lowe's)
  3. Mock (dev fallback)
"""
from .serpapi_scraper import SerpAPIScraper
from .homedepot_scraper import HomeDepotScraper
from .lowes_scraper import LowesScraper
from .mock_scraper import MockScraper

_hd = HomeDepotScraper()
_lowes = LowesScraper()
_mock = MockScraper()

STORE_SCRAPERS = {
    'Home Depot': [None, _hd],  # None placeholder replaced by SerpAPIScraper at call time
    "Lowe's": [None, _lowes],
    'Facebook Marketplace': [],   # manual-only
    'Local Store': [],             # manual-only
}


def fetch_price(item_name, store_name, zip_code=None):
    """Try each scraper in order; return first successful result or None."""
    _serpapi = SerpAPIScraper(zip_code=zip_code)
    store_scrapers = {
        'Home Depot': [_serpapi, _hd],
        "Lowe's": [_serpapi, _lowes],
        'Facebook Marketplace': [],
        'Local Store': [],
    }
    scrapers = store_scrapers.get(store_name, [])
    for scraper in scrapers:
        result = scraper.fetch_price(item_name, store_name, zip_code=zip_code)
        if result and result.get('price_per_unit', 0) > 0:
            return result
    return None
