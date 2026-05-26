import enum
from datetime import datetime
from app.extensions import db


class AvailabilityStatus(enum.Enum):
    IN_STOCK = 'in_stock'
    OUT_OF_STOCK = 'out_of_stock'
    LIMITED = 'limited'
    UNKNOWN = 'unknown'


class PriceResult(db.Model):
    __tablename__ = 'price_results'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('material_items.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store_sources.id'), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float)
    product_name = db.Column(db.String(300))
    product_url = db.Column(db.String(500))
    availability = db.Column(db.Enum(AvailabilityStatus), default=AvailabilityStatus.UNKNOWN)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_manual = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<PriceResult item={self.item_id} store={self.store_id} price={self.price_per_unit}>'
