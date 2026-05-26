from collections import defaultdict
from app.repositories.price_repository import PriceRepository
from app.repositories.material_repository import MaterialRepository
from app.models.price_result import PriceResult, AvailabilityStatus
from app.scrapers.mock_scraper import MockScraper
from datetime import datetime

price_repo = PriceRepository()
mat_repo = MaterialRepository()


class CompareService:
    def get_stores(self):
        return price_repo.get_stores()

    def build_matrix(self, project):
        stores = self.get_stores()
        store_map = {s.id: s for s in stores}
        matrix = {}  # list_name -> [row dicts]
        optimizer_data = {
            'store_totals': defaultdict(float),
            'list_subtotals': defaultdict(lambda: defaultdict(float)),
            'mix_breakdown': defaultdict(list),
            'best_mix_total': 0.0,
            'min_single_store': None,
            'max_total': None,
            'max_savings': 0.0,
        }

        for mat_list in project.material_lists:
            rows = []
            for item in mat_list.items:
                prices_by_store = {}
                for pr in item.price_results:
                    if pr.store_id in store_map:
                        prices_by_store[pr.store_id] = {
                            'unit_price': pr.price_per_unit,
                            'total': pr.total_price or pr.price_per_unit * item.quantity,
                        }

                totals = [v['total'] for v in prices_by_store.values()]
                best_total = min(totals) if totals else None
                worst_total = max(totals) if totals else None
                best_store_id = None
                best_store_name = None
                if best_total is not None:
                    for sid, pdata in prices_by_store.items():
                        if pdata['total'] == best_total:
                            best_store_id = sid
                            best_store_name = store_map[sid].name
                            break

                row = {
                    'item_id': item.id,
                    'item_name': item.name,
                    'quantity': item.quantity,
                    'unit': item.unit.value,
                    'prices': prices_by_store,
                    'best_total': best_total,
                    'worst_total': worst_total,
                    'best_store': best_store_name,
                    'best_store_id': best_store_id,
                }
                rows.append(row)

                # Accumulate optimizer data
                for sid, pdata in prices_by_store.items():
                    store_name = store_map[sid].name
                    optimizer_data['store_totals'][store_name] += pdata['total']
                    optimizer_data['list_subtotals'][mat_list.name][sid] += pdata['total']

                if best_store_name and best_total is not None:
                    optimizer_data['mix_breakdown'][best_store_name].append(
                        (item.name, best_total)
                    )
                    optimizer_data['best_mix_total'] += best_total

            if rows:
                matrix[mat_list.name] = rows

        # Compute min/max single store
        store_totals = dict(optimizer_data['store_totals'])
        if store_totals:
            min_val = min(store_totals.values())
            max_val = max(store_totals.values())
            optimizer_data['min_single_store'] = min_val
            optimizer_data['max_total'] = max_val
            optimizer_data['max_savings'] = max_val - optimizer_data['best_mix_total']

        # Convert defaultdicts for template
        optimizer_data['store_totals'] = store_totals
        optimizer_data['list_subtotals'] = {
            k: dict(v) for k, v in optimizer_data['list_subtotals'].items()
        }
        optimizer_data['mix_breakdown'] = dict(optimizer_data['mix_breakdown'])

        return matrix, stores, optimizer_data

    def refresh_prices(self, project):
        """Use mock scraper for dev; real scrapers can be swapped in later."""
        scraper = MockScraper()
        for mat_list in project.material_lists:
            for item in mat_list.items:
                stores = price_repo.get_stores()
                price_repo.delete_prices_for_item(item.id)
                results = []
                for store in stores:
                    data = scraper.fetch_price(item.name, store.name)
                    pr = PriceResult(
                        item_id=item.id,
                        store_id=store.id,
                        price_per_unit=data['price_per_unit'],
                        total_price=data['price_per_unit'] * item.quantity,
                        product_name=data['product_name'],
                        availability=AvailabilityStatus.IN_STOCK,
                        fetched_at=datetime.utcnow(),
                        is_manual=False,
                    )
                    results.append(pr)
                price_repo.bulk_save(results)
