from app.models.project import Project
from app.extensions import db


class ProjectRepository:
    def get_all_for_user(self, user_id):
        return Project.query.filter_by(user_id=user_id).order_by(Project.created_at.desc()).all()

    def get_by_id(self, project_id):
        return Project.query.get(project_id)

    def save(self, project):
        db.session.add(project)
        db.session.commit()
        return project

    def delete(self, project):
        db.session.delete(project)
        db.session.commit()
