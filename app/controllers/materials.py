from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.forms.material_forms import MaterialListForm, MaterialItemForm
from app.services.material_service import MaterialService
from app.services.project_service import ProjectService

materials_bp = Blueprint('materials', __name__)
material_service = MaterialService()
project_service = ProjectService()


@materials_bp.route('/projects/<int:project_id>/materials')
@login_required
def index(project_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    material_lists = material_service.get_lists(project_id)
    list_form = MaterialListForm()
    item_form = MaterialItemForm()
    return render_template('materials/index.html',
                           project=project,
                           material_lists=material_lists,
                           list_form=list_form,
                           item_form=item_form)


@materials_bp.route('/projects/<int:project_id>/materials/lists/create', methods=['POST'])
@login_required
def create_list(project_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    form = MaterialListForm()
    if form.validate_on_submit():
        material_service.create_list(project_id, form.name.data)
        flash('List added!', 'success')
    return redirect(url_for('materials.index', project_id=project_id))


@materials_bp.route('/projects/<int:project_id>/materials/lists/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_list(project_id, list_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    material_service.delete_list(list_id)
    flash('List deleted.', 'info')
    return redirect(url_for('materials.index', project_id=project_id))


@materials_bp.route('/projects/<int:project_id>/materials/lists/<int:list_id>/items/add', methods=['POST'])
@login_required
def add_item(project_id, list_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    form = MaterialItemForm()
    if form.validate_on_submit():
        material_service.add_item(list_id, {
            'name': form.name.data,
            'quantity': form.quantity.data,
            'unit': form.unit.data,
        })
        flash('Item added!', 'success')
    return redirect(url_for('materials.index', project_id=project_id))


@materials_bp.route('/projects/<int:project_id>/materials/lists/<int:list_id>/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(project_id, list_id, item_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    material_service.delete_item(item_id)
    flash('Item removed.', 'info')
    return redirect(url_for('materials.index', project_id=project_id))
