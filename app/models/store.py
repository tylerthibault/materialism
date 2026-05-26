import enum
from app.extensions import db


project_stores = db.Table('project_stores',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('store_id', db.Integer, db.ForeignKey('store_sources.id'), primary_key=True)
)


class StoreType(enum.Enum):
    HOME_DEPOT = 'home_depot'
    LOWES = 'lowes'
    LOCAL = 'local'
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
