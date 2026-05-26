from app.models.price_result import PriceResult
from app.models.store import StoreSource
from app.extensions import db


class PriceRepository:
    def get_prices_for_item(self, item_id):
        return PriceResult.query.filter_by(item_id=item_id).all()

    def get_stores(self):
        return StoreSource.query.filter_by(is_active=True).all()

    def delete_prices_for_item(self, item_id):
        PriceResult.query.filter_by(item_id=item_id).delete()
        db.session.commit()

    def save(self, price_result):
        db.session.add(price_result)
        db.session.commit()
        return price_result

    def bulk_save(self, results):
        for r in results:
            db.session.add(r)
        db.session.commit()
