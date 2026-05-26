"""Tests for all SQLAlchemy models."""
import pytest
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus
from app.models.material_list import MaterialList
from app.models.material_item import MaterialItem, UnitType
from app.models.store import StoreSource, StoreType
from app.models.price_result import PriceResult, AvailabilityStatus
from datetime import datetime


class TestUserModel:
    def test_user_creates_with_required_fields(self, db):
        u = User(email='new@example.com', name='New User', company_name='Co', role=UserRole.USER)
        u.set_password('secret')
        db.session.add(u)
        db.session.commit()
        assert u.id is not None
        assert u.email == 'new@example.com'

    def test_password_hashing_does_not_store_plaintext(self, db):
        u = User(email='hash@example.com', name='Hash User', company_name='Co', role=UserRole.USER)
        u.set_password('mypassword')
        assert u.password_hash != 'mypassword'
        assert u.password_hash is not None

    def test_check_password_returns_true_for_correct_password(self, db):
        u = User(email='check@example.com', name='Check User', company_name='Co', role=UserRole.USER)
        u.set_password('correct')
        assert u.check_password('correct') is True

    def test_check_password_returns_false_for_wrong_password(self, db):
        u = User(email='wrong@example.com', name='Wrong User', company_name='Co', role=UserRole.USER)
        u.set_password('correct')
        assert u.check_password('wrong') is False

    def test_user_email_must_be_unique(self, db, user):
        duplicate = User(email='test@example.com', name='Dup', company_name='Co', role=UserRole.USER)
        duplicate.set_password('pass')
        db.session.add(duplicate)
        with pytest.raises(Exception):
            db.session.commit()

    def test_user_defaults_to_user_role(self, db):
        u = User(email='role@example.com', name='Role User', company_name='Co', role=UserRole.USER)
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()
        assert u.role == UserRole.USER

    def test_user_has_projects_relationship(self, db, user, project):
        assert len(user.projects) == 1
        assert user.projects[0].name == 'Test Project'


class TestProjectModel:
    def test_project_creates_with_required_fields(self, db, user):
        p = Project(user_id=user.id, name='New Project', client_name='Client',
                    location='Portland, OR', status=ProjectStatus.ACTIVE)
        db.session.add(p)
        db.session.commit()
        assert p.id is not None

    def test_project_default_status_is_active(self, db, user):
        p = Project(user_id=user.id, name='Status Test', client_name='Client',
                    location='Anywhere', status=ProjectStatus.ACTIVE)
        db.session.add(p)
        db.session.commit()
        assert p.status == ProjectStatus.ACTIVE

    def test_project_has_material_lists_relationship(self, db, project, material_list):
        assert len(project.material_lists) == 1
        assert project.material_lists[0].name == 'Framing'

    def test_deleting_project_cascades_to_material_lists(self, db, project, material_list):
        project_id = project.id
        list_id = material_list.id
        db.session.delete(project)
        db.session.commit()
        assert MaterialList.query.get(list_id) is None


class TestMaterialListModel:
    def test_material_list_creates_with_name(self, db, project):
        ml = MaterialList(project_id=project.id, name='Electrical')
        db.session.add(ml)
        db.session.commit()
        assert ml.id is not None
        assert ml.name == 'Electrical'

    def test_material_list_has_items_relationship(self, db, material_list, material_item):
        assert len(material_list.items) == 1
        assert material_list.items[0].name == '2x4x8 Stud'


class TestMaterialItemModel:
    def test_material_item_creates_with_required_fields(self, db, material_list):
        item = MaterialItem(list_id=material_list.id, name='OSB Sheet', quantity=20, unit=UnitType.SHEET)
        db.session.add(item)
        db.session.commit()
        assert item.id is not None

    def test_material_item_default_unit_is_each(self, db, material_list):
        item = MaterialItem(list_id=material_list.id, name='Bolt', quantity=100, unit=UnitType.EACH)
        db.session.add(item)
        db.session.commit()
        assert item.unit == UnitType.EACH

    def test_material_item_stores_float_quantity(self, db, material_list):
        item = MaterialItem(list_id=material_list.id, name='Lumber', quantity=12.5, unit=UnitType.LF)
        db.session.add(item)
        db.session.commit()
        assert item.quantity == 12.5

    def test_material_item_has_price_results_relationship(self, db, material_item, price_results):
        assert len(material_item.price_results) == 3


class TestStoreSourceModel:
    def test_store_creates_with_required_fields(self, db):
        s = StoreSource(name='Test Store', store_type=StoreType.LOCAL, website_url='', is_active=True, supports_scraping=False)
        db.session.add(s)
        db.session.commit()
        assert s.id is not None

    def test_stores_fixture_creates_all_three(self, db, stores):
        assert len(stores) == 3
        types = {s.store_type for s in stores}
        assert StoreType.HOME_DEPOT in types
        assert StoreType.LOWES in types
        assert StoreType.LOCAL in types


class TestPriceResultModel:
    def test_price_result_creates_with_required_fields(self, db, material_item, stores):
        pr = PriceResult(
            item_id=material_item.id, store_id=stores[0].id,
            price_per_unit=9.99, total_price=99.90,
            product_name='Test Item', availability=AvailabilityStatus.IN_STOCK,
            fetched_at=datetime.utcnow(), is_manual=False
        )
        db.session.add(pr)
        db.session.commit()
        assert pr.id is not None

    def test_price_result_links_to_item(self, db, price_results, material_item):
        assert price_results[0].item_id == material_item.id

    def test_price_result_links_to_store(self, db, price_results, stores):
        assert price_results[0].store_id == stores[0].id

    def test_deleting_item_cascades_to_price_results(self, db, material_item, price_results):
        item_id = material_item.id
        db.session.delete(material_item)
        db.session.commit()
        remaining = PriceResult.query.filter_by(item_id=item_id).all()
        assert len(remaining) == 0
