import os
import re
import requests
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, jsonify
from flask_login import login_required, current_user
from app.forms.material_forms import MaterialListForm, MaterialItemForm
from app.services.material_service import MaterialService
from app.services.project_service import ProjectService

materials_bp = Blueprint('materials', __name__)
material_service = MaterialService()
project_service = ProjectService()

SERPAPI_BASE = 'https://serpapi.com/search'
SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '')


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
        hd_product_name = request.form.get('hd_product_name', '')
        hd_product_url = request.form.get('hd_product_url', '')
        hd_product_price = request.form.get('hd_product_price', '')
        lowes_product_name = request.form.get('lowes_product_name', '')
        lowes_product_url = request.form.get('lowes_product_url', '')
        lowes_product_price = request.form.get('lowes_product_price', '')
        material_service.add_item(list_id, {
            'name': form.name.data,
            'quantity': form.quantity.data,
            'unit': form.unit.data,
            'hd_product_name': hd_product_name,
            'hd_product_url': hd_product_url,
            'hd_product_price': hd_product_price,
            'lowes_product_name': lowes_product_name,
            'lowes_product_url': lowes_product_url,
            'lowes_product_price': lowes_product_price,
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


@materials_bp.route('/api/projects/<int:project_id>/search-products')
@login_required
def search_products(project_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)

    q = request.args.get('q', '').strip()
    if not q or not SERPAPI_KEY:
        return jsonify({'hd': [], 'lowes': []})

    zip_code = project.zip_code or ''

    hd_results = []
    lowes_results = []

    # Home Depot search
    try:
        params = {
            'engine': 'home_depot',
            'q': q,
            'api_key': SERPAPI_KEY,
        }
        if zip_code:
            params['delivery_zip'] = zip_code
        resp = requests.get(SERPAPI_BASE, params=params, timeout=12)
        resp.raise_for_status()
        data = resp.json()
        products = data.get('products') or data.get('products_results') or []
        for p in products[:6]:
            item_id = p.get('item_id', '')
            # Build proper storefront URL from item_id; avoid internal apionline.homedepot.com links
            if item_id:
                title_slug = re.sub(r'[^a-zA-Z0-9]+', '-', p.get('title', '')).strip('-')
                url = f"https://www.homedepot.com/p/{title_slug}/{item_id}"
            else:
                raw_url = p.get('link', '')
                # Replace internal API URLs with a generic search URL
                if 'apionline.homedepot.com' in raw_url or not raw_url.startswith('https://www.homedepot.com'):
                    url = f"https://www.homedepot.com/s/{requests.utils.quote(p.get('title', q))}"
                else:
                    url = raw_url
            hd_results.append({
                'title': p.get('title', ''),
                'price': p.get('price', ''),
                'url': url,
                'thumbnail': p.get('thumbnail', ''),
            })
    except Exception:
        pass

    # Lowe's search via Google Shopping
    try:
        params = {
            'engine': 'google_shopping',
            'q': f'{q} lowes',
            'api_key': SERPAPI_KEY,
        }
        if zip_code:
            params['location'] = zip_code
        resp = requests.get(SERPAPI_BASE, params=params, timeout=12)
        resp.raise_for_status()
        data = resp.json()
        results = data.get('shopping_results', [])
        lowes_only = [r for r in results if 'lowe' in (r.get('source') or '').lower()]
        pool = lowes_only if lowes_only else results
        for p in pool[:6]:
            lowes_results.append({
                'title': p.get('title', ''),
                'price': p.get('price', ''),
                'url': p.get('link', ''),
                'thumbnail': p.get('thumbnail', ''),
            })
    except Exception:
        pass

    return jsonify({'hd': hd_results, 'lowes': lowes_results})


@materials_bp.route('/api/projects/<int:project_id>/items/<int:item_id>/pin-product', methods=['POST'])
@login_required
def pin_product(project_id, item_id):
    project = project_service.get_project(project_id)
    if not project or project.user_id != current_user.id:
        abort(404)
    body = request.get_json(force=True, silent=True) or {}
    store = body.get('store', '')
    product_name = body.get('product_name', '')
    product_url = body.get('product_url', '')
    product_price = body.get('product_price')
    material_service.pin_product(item_id, store, product_name, product_url, product_price)
    return jsonify({'success': True})
