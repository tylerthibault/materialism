from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.forms.project_forms import ProjectForm
from app.services.project_service import ProjectService
from app.models.project import ProjectStatus

projects_bp = Blueprint('projects', __name__)
project_service = ProjectService()


@projects_bp.route('/')
@login_required
def index():
    projects = project_service.get_user_projects(current_user.id)
    return render_template('projects/index.html', projects=projects)


@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ProjectForm()
    if form.validate_on_submit():
        project_service.create_project(current_user.id, {
            'name': form.name.data,
            'client_name': form.client_name.data,
            'location': form.location.data,
            'zip_code': form.zip_code.data,
            'description': form.description.data,
        })
        flash('Project created!', 'success')
        return redirect(url_for('projects.index'))
    return render_template('projects/form.html', form=form, project=None)


@projects_bp.route('/<int:project_id>')
@login_required
def detail(project_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    return render_template('projects/detail.html', project=project)


@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project_service.update_project(project, {
            'name': form.name.data,
            'client_name': form.client_name.data,
            'location': form.location.data,
            'zip_code': form.zip_code.data,
            'description': form.description.data,
            'status': form.status.data,
        })
        flash('Project updated!', 'success')
        return redirect(url_for('projects.detail', project_id=project.id))
    # Pre-populate status
    form.status.data = project.status.value
    return render_template('projects/form.html', form=form, project=project)


@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete(project_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    project_service.delete_project(project)
    flash('Project deleted.', 'info')
    return redirect(url_for('projects.index'))
