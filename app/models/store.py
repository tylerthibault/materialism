import enum
from app.extensions import db


class StoreType(enum.Enum):
    HOME_DEPOT = 'home_depot'
    LOWES = 'lowes'
    LOCAL = 'local'
    FACEBOOK = 'facebook'
    OTHER = 'other'


class StoreSource(db.Model):
    __tablename__ = 'store_sources'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    store_type = db.Column(db.Enum(StoreType), nullable=False)
    website_url = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)
    supports_scraping = db.Column(db.Boolean, default=False)

    price_results = db.relationship('PriceResult', backref='store', lazy=True)

    def __repr__(self):
        return f'<StoreSource {self.name}>'
