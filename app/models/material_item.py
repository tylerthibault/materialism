import enum
from datetime import datetime
from app.extensions import db


class UnitType(enum.Enum):
    EACH = 'each'
    SHEET = 'sheet'
    BAG = 'bag'
    LF = 'lf'
    SF = 'sf'
    LB = 'lb'
    TON = 'ton'
    GALLON = 'gallon'
    BOX = 'box'
    BUNDLE = 'bundle'


class MaterialItem(db.Model):
    __tablename__ = 'material_items'

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('material_lists.id'), nullable=False)
    name = db.Column(db.String(300), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1)
    unit = db.Column(db.Enum(UnitType), default=UnitType.EACH, nullable=False)
    notes = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Pinned products per store
    hd_product_name = db.Column(db.String(500))
    hd_product_url = db.Column(db.String(1000))
    hd_product_price = db.Column(db.Float)
    lowes_product_name = db.Column(db.String(500))
    lowes_product_url = db.Column(db.String(1000))
    lowes_product_price = db.Column(db.Float)

    price_results = db.relationship('PriceResult', backref='item', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<MaterialItem {self.name}>'
