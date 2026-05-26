from app.models.material_list import MaterialList
from app.models.material_item import MaterialItem, UnitType
from app.repositories.material_repository import MaterialRepository
from app.extensions import db

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

        def _parse_price(val):
            try:
                return float(val) if val else None
            except (ValueError, TypeError):
                return None

        item = MaterialItem(
            list_id=list_id,
            name=form_data['name'],
            quantity=float(form_data.get('quantity', 1)),
            unit=unit,
            hd_product_name=form_data.get('hd_product_name') or None,
            hd_product_url=form_data.get('hd_product_url') or None,
            hd_product_price=_parse_price(form_data.get('hd_product_price')),
            lowes_product_name=form_data.get('lowes_product_name') or None,
            lowes_product_url=form_data.get('lowes_product_url') or None,
            lowes_product_price=_parse_price(form_data.get('lowes_product_price')),
        )
        return repo.save_item(item)

    def delete_item(self, item_id):
        item = repo.get_item_by_id(item_id)
        if item:
            repo.delete_item(item)

    def pin_product(self, item_id, store, product_name, product_url, product_price):
        item = repo.get_item_by_id(item_id)
        if not item:
            return
        if store == 'hd':
            item.hd_product_name = product_name or None
            item.hd_product_url = product_url or None
            item.hd_product_price = float(product_price) if product_price else None
        elif store == 'lowes':
            item.lowes_product_name = product_name or None
            item.lowes_product_url = product_url or None
            item.lowes_product_price = float(product_price) if product_price else None
        db.session.commit()
