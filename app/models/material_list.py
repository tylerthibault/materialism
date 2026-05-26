from datetime import datetime
from app.extensions import db


class MaterialList(db.Model):
    __tablename__ = 'material_lists'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('MaterialItem', backref='material_list', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<MaterialList {self.name}>'
