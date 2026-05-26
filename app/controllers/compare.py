from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.services.compare_service import CompareService
from app.services.project_service import ProjectService

compare_bp = Blueprint('compare', __name__)
compare_service = CompareService()
project_service = ProjectService()


@compare_bp.route('/projects/<int:project_id>/compare')
@login_required
def matrix(project_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    matrix, stores, optimizer = compare_service.build_matrix(project)
    return render_template('compare/matrix.html',
                           project=project,
                           matrix=matrix,
                           stores=stores,
                           optimizer=optimizer)


@compare_bp.route('/projects/<int:project_id>/compare/refresh', methods=['POST'])
@login_required
def refresh(project_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    compare_service.refresh_prices(project)
    flash('Prices refreshed!', 'success')
    return redirect(url_for('compare.matrix', project_id=project_id))
