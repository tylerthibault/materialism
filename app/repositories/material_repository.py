from app.models.material_list import MaterialList
from app.models.material_item import MaterialItem
from app.extensions import db


class MaterialRepository:
    def get_lists_for_project(self, project_id):
        return MaterialList.query.filter_by(project_id=project_id).all()

    def get_list_by_id(self, list_id):
        return MaterialList.query.get(list_id)

    def save_list(self, mat_list):
        db.session.add(mat_list)
        db.session.commit()
        return mat_list

    def delete_list(self, mat_list):
        db.session.delete(mat_list)
        db.session.commit()

    def get_item_by_id(self, item_id):
        return MaterialItem.query.get(item_id)

    def save_item(self, item):
        db.session.add(item)
        db.session.commit()
        return item

    def delete_item(self, item):
        db.session.delete(item)
        db.session.commit()
