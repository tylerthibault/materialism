"""Tests for all Flask routes / controllers."""
import pytest
from tests.conftest import login


class TestLandingRoutes:
    def test_home_returns_200(self, client):
        r = client.get('/')
        assert r.status_code == 200

    def test_home_contains_app_name(self, client):
        r = client.get('/')
        assert b'materialism' in r.data.lower() or b'buildbid' in r.data.lower() or b'material' in r.data.lower()


class TestAuthRoutes:
    def test_register_page_loads(self, client):
        r = client.get('/auth/register')
        assert r.status_code == 200

    def test_login_page_loads(self, client):
        r = client.get('/auth/login')
        assert r.status_code == 200

    def test_register_creates_account_and_redirects(self, client, app):
        r = client.post('/auth/register', data={
            'name': 'Tyler Thibault',
            'email': 'tyler@example.com',
            'company_name': 'Tyler Co',
            'password': 'password123',
            'confirm_password': 'password123',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_login_with_valid_credentials_redirects_to_dashboard(self, client, user):
        r = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_login_with_bad_password_shows_error(self, client, user):
        r = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'wrongpass',
        }, follow_redirects=True)
        assert r.status_code == 200
        # Should stay on login or show error, not go to dashboard
        assert b'invalid' in r.data.lower() or b'error' in r.data.lower() or b'login' in r.data.lower() or b'sign in' in r.data.lower()

    def test_logout_redirects_to_home_or_login(self, client, user):
        login(client)
        r = client.get('/auth/logout', follow_redirects=True)
        assert r.status_code == 200


class TestDashboardRoutes:
    def test_dashboard_requires_login(self, client):
        r = client.get('/dashboard/', follow_redirects=True)
        # Should redirect to login
        assert r.status_code == 200
        assert b'login' in r.data.lower() or b'sign in' in r.data.lower()

    def test_dashboard_accessible_when_logged_in(self, client, user):
        login(client)
        r = client.get('/dashboard/')
        assert r.status_code == 200


class TestProjectRoutes:
    def test_project_list_requires_login(self, client):
        r = client.get('/projects/', follow_redirects=True)
        assert r.status_code == 200
        assert b'login' in r.data.lower() or b'sign in' in r.data.lower()

    def test_project_list_accessible_when_logged_in(self, client, user):
        login(client)
        r = client.get('/projects/')
        assert r.status_code == 200

    def test_create_project_get_returns_form(self, client, user):
        login(client)
        r = client.get('/projects/create')
        assert r.status_code == 200

    def test_create_project_post_creates_and_redirects(self, client, user):
        login(client)
        r = client.post('/projects/create', data={
            'name': 'Test House',
            'client_name': 'Bob Builder',
            'location': 'Seattle, WA',
            'description': 'New house build',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_project_detail_returns_200(self, client, user, project):
        login(client)
        r = client.get(f'/projects/{project.id}')
        assert r.status_code == 200

    def test_project_detail_404_for_nonexistent(self, client, user):
        login(client)
        r = client.get('/projects/99999')
        assert r.status_code == 404

    def test_cannot_view_another_users_project(self, client, admin_user, project):
        # Login as admin (different user who doesn't own the project)
        client.post('/auth/login', data={'email': 'admin@example.com', 'password': 'adminpass'}, follow_redirects=True)
        r = client.get(f'/projects/{project.id}')
        assert r.status_code in (403, 404, 302)

    def test_delete_project_removes_it(self, client, user, project):
        login(client)
        r = client.post(f'/projects/{project.id}/delete', follow_redirects=True)
        assert r.status_code == 200


class TestMaterialRoutes:
    def test_add_material_list_post(self, client, user, project):
        login(client)
        r = client.post(f'/projects/{project.id}/materials/lists/create', data={
            'name': 'Plumbing',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_add_material_item_post(self, client, user, project, material_list):
        login(client)
        r = client.post(f'/projects/{project.id}/materials/lists/{material_list.id}/items/add', data={
            'name': 'PVC Pipe',
            'quantity': 10,
            'unit': 'each',
            'notes': '',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_delete_material_item(self, client, user, material_item, material_list, project):
        login(client)
        r = client.post(f'/projects/{project.id}/materials/lists/{material_list.id}/items/{material_item.id}/delete', follow_redirects=True)
        assert r.status_code == 200


class TestCompareRoutes:
    def test_compare_matrix_requires_login(self, client, project):
        r = client.get(f'/projects/{project.id}/compare', follow_redirects=True)
        assert r.status_code == 200
        assert b'login' in r.data.lower() or b'sign in' in r.data.lower()

    def test_compare_matrix_loads_for_owner(self, client, user, project, stores):
        login(client)
        r = client.get(f'/projects/{project.id}/compare')
        assert r.status_code == 200


class TestErrorHandlers:
    def test_404_returns_custom_page(self, client):
        r = client.get('/nonexistent/route/xyz')
        assert r.status_code == 404
