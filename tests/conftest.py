import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus
from app.models.material_list import MaterialList
from app.models.material_item import MaterialItem, UnitType
from app.models.store import StoreSource, StoreType
from app.models.price_result import PriceResult, AvailabilityStatus
from datetime import datetime


@pytest.fixture(scope='function')
def app():
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret',
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    return _db


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def user(db):
    u = User(email='test@example.com', name='Test User', company_name='Test Co', role=UserRole.USER)
    u.set_password('password123')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture(scope='function')
def admin_user(db):
    u = User(email='admin@example.com', name='Admin User', company_name='Admin Co', role=UserRole.ADMIN)
    u.set_password('adminpass')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture(scope='function')
def project(db, user):
    p = Project(user_id=user.id, name='Test Project', client_name='Test Client',
                location='Seattle, WA', description='A test project', status=ProjectStatus.ACTIVE)
    db.session.add(p)
    db.session.commit()
    return p


@pytest.fixture(scope='function')
def material_list(db, project):
    ml = MaterialList(project_id=project.id, name='Framing')
    db.session.add(ml)
    db.session.commit()
    return ml


@pytest.fixture(scope='function')
def material_item(db, material_list):
    item = MaterialItem(list_id=material_list.id, name='2x4x8 Stud', quantity=50, unit=UnitType.EACH)
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture(scope='function')
def stores(db):
    store_list = [
        StoreSource(name='Home Depot', store_type=StoreType.HOME_DEPOT, website_url='https://homedepot.com', is_active=True, supports_scraping=True),
        StoreSource(name="Lowe's", store_type=StoreType.LOWES, website_url='https://lowes.com', is_active=True, supports_scraping=True),
        StoreSource(name='Local Store', store_type=StoreType.LOCAL, website_url='', is_active=True, supports_scraping=False),
    ]
    db.session.add_all(store_list)
    db.session.commit()
    return store_list


@pytest.fixture(scope='function')
def price_results(db, material_item, stores):
    hd, lowes, local = stores
    results = [
        PriceResult(item_id=material_item.id, store_id=hd.id, price_per_unit=4.98, total_price=249.00, product_name='2x4x8 Stud', availability=AvailabilityStatus.IN_STOCK, fetched_at=datetime.utcnow(), is_manual=False),
        PriceResult(item_id=material_item.id, store_id=lowes.id, price_per_unit=5.12, total_price=256.00, product_name='2x4x8 Stud', availability=AvailabilityStatus.IN_STOCK, fetched_at=datetime.utcnow(), is_manual=False),
        PriceResult(item_id=material_item.id, store_id=local.id, price_per_unit=4.50, total_price=225.00, product_name='2x4x8 Stud', availability=AvailabilityStatus.IN_STOCK, fetched_at=datetime.utcnow(), is_manual=False),
    ]
    db.session.add_all(results)
    db.session.commit()
    return results


def login(client, email='test@example.com', password='password123'):
    return client.post('/auth/login', data={'email': email, 'password': password}, follow_redirects=True)
