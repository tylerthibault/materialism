"""Mock scraper for development — returns fake prices."""
import random


class MockScraper:
    def fetch_price(self, item_name, store_name='Mock Store'):
        base = random.uniform(5, 200)
        return {
            'price_per_unit': round(base, 2),
            'product_name': item_name,
            'product_url': '',
            'availability': 'in_stock',
        }
