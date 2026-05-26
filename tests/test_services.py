"""Tests for service layer."""
import pytest
from app.services.auth_service import AuthService
from app.services.project_service import ProjectService
from app.services.material_service import MaterialService
from app.services.compare_service import CompareService
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.material_item import MaterialItem


class TestAuthService:
    def test_register_creates_user(self, app, db):
        svc = AuthService()
        with app.app_context():
            u = svc.register({'email': 'new@example.com', 'name': 'New', 'company_name': 'Co', 'password': 'pass'})
            assert u.id is not None
            assert u.email == 'new@example.com'

    def test_register_hashes_password(self, app, db):
        svc = AuthService()
        with app.app_context():
            u = svc.register({'email': 'hash@example.com', 'name': 'Hash', 'company_name': 'Co', 'password': 'secret'})
            assert u.password_hash != 'secret'

    def test_login_returns_user_with_correct_credentials(self, app, db, user):
        svc = AuthService()
        with app.app_context():
            result = svc.login('test@example.com', 'password123')
            assert result is not None
            assert result.email == 'test@example.com'

    def test_login_returns_none_with_wrong_password(self, app, db, user):
        svc = AuthService()
        with app.app_context():
            result = svc.login('test@example.com', 'wrongpassword')
            assert result is None

    def test_login_returns_none_for_unknown_email(self, app, db):
        svc = AuthService()
        with app.app_context():
            result = svc.login('nobody@example.com', 'pass')
            assert result is None


class TestProjectService:
    def test_create_project_persists_to_db(self, app, db, user):
        svc = ProjectService()
        with app.app_context():
            p = svc.create_project(user.id, {
                'name': 'Kitchen Reno',
                'client_name': 'Smith Family',
                'location': 'Tacoma, WA',
                'description': 'Full kitchen remodel',
            })
            assert p.id is not None
            assert p.name == 'Kitchen Reno'

    def test_create_project_links_to_user(self, app, db, user):
        svc = ProjectService()
        with app.app_context():
            p = svc.create_project(user.id, {
                'name': 'Deck Build',
                'client_name': 'Jones',
                'location': 'Spokane, WA',
                'description': '',
            })
            assert p.user_id == user.id

    def test_get_user_projects_returns_only_their_projects(self, app, db, user, admin_user):
        svc = ProjectService()
        with app.app_context():
            svc.create_project(user.id, {'name': 'P1', 'client_name': 'C1', 'location': 'L1', 'description': ''})
            svc.create_project(user.id, {'name': 'P2', 'client_name': 'C2', 'location': 'L2', 'description': ''})
            svc.create_project(admin_user.id, {'name': 'Admin P', 'client_name': 'Admin C', 'location': 'L3', 'description': ''})
            projects = svc.get_user_projects(user.id)
            assert len(projects) == 2
            assert all(p.user_id == user.id for p in projects)

    def test_delete_project_removes_from_db(self, app, db, project):
        svc = ProjectService()
        with app.app_context():
            p = Project.query.get(project.id)
            pid = p.id
            svc.delete_project(p)
            assert Project.query.get(pid) is None


class TestMaterialService:
    def test_add_item_to_list(self, app, db, material_list):
        svc = MaterialService()
        with app.app_context():
            item = svc.add_item(material_list.id, {
                'name': 'Concrete Block',
                'quantity': 100,
                'unit': 'each',
                'notes': '',
            })
            assert item.id is not None
            assert item.name == 'Concrete Block'
            assert item.list_id == material_list.id

    def test_add_item_stores_quantity(self, app, db, material_list):
        svc = MaterialService()
        with app.app_context():
            item = svc.add_item(material_list.id, {'name': 'Rebar', 'quantity': 25, 'unit': 'each', 'notes': ''})
            assert item.quantity == 25

    def test_delete_item_removes_from_db(self, app, db, material_item):
        svc = MaterialService()
        with app.app_context():
            iid = material_item.id
            svc.delete_item(iid)
            assert MaterialItem.query.get(iid) is None


class TestCompareService:
    def test_build_matrix_returns_matrix_and_stores(self, app, db, project, material_list, material_item, stores, price_results):
        svc = CompareService()
        with app.app_context():
            # Refresh relationships
            p = Project.query.get(project.id)
            matrix, store_list, optimizer = svc.build_matrix(p)
            assert isinstance(matrix, dict)
            assert len(matrix) >= 1

    def test_build_matrix_rows_contain_prices(self, app, db, project, material_list, material_item, stores, price_results):
        svc = CompareService()
        with app.app_context():
            p = Project.query.get(project.id)
            matrix, store_list, optimizer = svc.build_matrix(p)
            rows = list(matrix.values())[0]
            row = rows[0]
            assert 'prices' in row
            assert len(row['prices']) == 3

    def test_build_matrix_identifies_best_price(self, app, db, project, material_list, material_item, stores, price_results):
        svc = CompareService()
        with app.app_context():
            p = Project.query.get(project.id)
            matrix, _, _ = svc.build_matrix(p)
            rows = list(matrix.values())[0]
            row = rows[0]
            # Local store has lowest price (4.50 * 50 = 225)
            assert row['best_total'] == 225.0

    def test_optimizer_data_has_store_totals(self, app, db, project, material_list, material_item, stores, price_results):
        svc = CompareService()
        with app.app_context():
            p = Project.query.get(project.id)
            _, _, optimizer = svc.build_matrix(p)
            assert 'store_totals' in optimizer
            assert len(optimizer['store_totals']) == 3

    def test_optimizer_best_mix_total_is_lowest(self, app, db, project, material_list, material_item, stores, price_results):
        svc = CompareService()
        with app.app_context():
            p = Project.query.get(project.id)
            _, _, optimizer = svc.build_matrix(p)
            # Best mix should be 225 (local store)
            assert optimizer['best_mix_total'] == 225.0

    def test_optimizer_max_savings_computed(self, app, db, project, material_list, material_item, stores, price_results):
        svc = CompareService()
        with app.app_context():
            p = Project.query.get(project.id)
            _, _, optimizer = svc.build_matrix(p)
            # Max savings = highest store total - best mix
            assert optimizer['max_savings'] >= 0
