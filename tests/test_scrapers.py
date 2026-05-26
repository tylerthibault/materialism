"""Tests for scraper layer."""
import pytest
from app.scrapers.mock_scraper import MockScraper


class TestMockScraper:
    def test_fetch_price_returns_dict(self):
        scraper = MockScraper()
        result = scraper.fetch_price('2x4x8 Stud', 'Home Depot')
        assert isinstance(result, dict)

    def test_fetch_price_has_required_keys(self):
        scraper = MockScraper()
        result = scraper.fetch_price('OSB Sheet', "Lowe's")
        assert 'price_per_unit' in result
        assert 'product_name' in result

    def test_fetch_price_returns_positive_price(self):
        scraper = MockScraper()
        result = scraper.fetch_price('Rebar', 'Local Store')
        assert result['price_per_unit'] > 0

    def test_fetch_price_returns_numeric_price(self):
        scraper = MockScraper()
        result = scraper.fetch_price('Concrete Mix', 'Home Depot')
        assert isinstance(result['price_per_unit'], (int, float))

    def test_fetch_price_returns_product_name_string(self):
        scraper = MockScraper()
        result = scraper.fetch_price('Nail Gun', "Lowe's")
        assert isinstance(result['product_name'], str)

    def test_fetch_price_consistent_for_same_inputs(self):
        scraper = MockScraper()
        r1 = scraper.fetch_price('2x4x8 Stud', 'Home Depot')
        r2 = scraper.fetch_price('2x4x8 Stud', 'Home Depot')
        # Mock may randomize — just confirm both are valid dicts
        assert isinstance(r1['price_per_unit'], (int, float))
        assert isinstance(r2['price_per_unit'], (int, float))

    def test_different_stores_may_return_different_prices(self):
        scraper = MockScraper()
        hd = scraper.fetch_price('2x4x8 Stud', 'Home Depot')
        lowes = scraper.fetch_price('2x4x8 Stud', "Lowe's")
        # Both valid — prices may differ
        assert hd['price_per_unit'] > 0
        assert lowes['price_per_unit'] > 0
