from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, jsonify
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
    compare_service.refresh_prices(project, zip_code=current_user.zip_code)
    flash('Live prices fetched from Home Depot and Lowe\'s!', 'success')
    return redirect(url_for('compare.matrix', project_id=project_id))


@compare_bp.route('/projects/<int:project_id>/compare/manual-price', methods=['POST'])
@login_required
def manual_price(project_id):
    """Save a manually entered price (Facebook Marketplace, local store, etc.)."""
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)

    item_id = request.form.get('item_id', type=int)
    store_id = request.form.get('store_id', type=int)
    price = request.form.get('price', type=float)
    notes = request.form.get('notes', '').strip()

    if not item_id or not store_id or price is None or price < 0:
        flash('Invalid price data.', 'danger')
        return redirect(url_for('compare.matrix', project_id=project_id))

    compare_service.set_manual_price(item_id, store_id, price, notes)
    flash('Manual price saved!', 'success')
    return redirect(url_for('compare.matrix', project_id=project_id))
