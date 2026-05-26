import enum
from datetime import datetime
from app.extensions import db


class ProjectStatus(enum.Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    ARCHIVED = 'archived'


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    client_name = db.Column(db.String(150))
    location = db.Column(db.String(200))
    zip_code = db.Column(db.String(10))
    description = db.Column(db.Text)
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    material_lists = db.relationship('MaterialList', backref='project', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.name}>'
