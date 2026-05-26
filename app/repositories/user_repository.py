from app.models.user import User
from app.extensions import db


class UserRepository:
    def get_by_id(self, user_id):
        return User.query.get(user_id)

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def save(self, user):
        db.session.add(user)
        db.session.commit()
        return user
