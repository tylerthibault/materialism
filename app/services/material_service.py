from app.models.material_list import MaterialList
from app.models.material_item import MaterialItem, UnitType
from app.repositories.material_repository import MaterialRepository

repo = MaterialRepository()


class MaterialService:
    def get_lists(self, project_id):
        return repo.get_lists_for_project(project_id)

    def create_list(self, project_id, name):
        mat_list = MaterialList(project_id=project_id, name=name)
        return repo.save_list(mat_list)

    def delete_list(self, list_id):
        mat_list = repo.get_list_by_id(list_id)
        if mat_list:
            repo.delete_list(mat_list)

    def add_item(self, list_id, form_data):
        unit_val = form_data.get('unit', UnitType.EACH.value)
        try:
            unit = UnitType(unit_val)
        except ValueError:
            unit = UnitType.EACH
        item = MaterialItem(
            list_id=list_id,
            name=form_data['name'],
            quantity=float(form_data.get('quantity', 1)),
            unit=unit,
        )
        return repo.save_item(item)

    def delete_item(self, item_id):
        item = repo.get_item_by_id(item_id)
        if item:
            repo.delete_item(item)
