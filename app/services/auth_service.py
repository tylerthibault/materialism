from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from flask_login import login_user, logout_user

repo = UserRepository()


class AuthService:
    def register(self, form_data):
        user = User(
            email=form_data['email'],
            name=form_data['name'],
            company_name=form_data.get('company_name', ''),
            role=UserRole.USER,
        )
        user.set_password(form_data['password'])
        repo.save(user)
        return user

    def login(self, email, password, remember=False):
        user = repo.get_by_email(email)
        if user and user.check_password(password):
            login_user(user, remember=remember)
            return user
        return None

    def logout(self):
        logout_user()
