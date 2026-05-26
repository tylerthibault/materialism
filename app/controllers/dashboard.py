from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.project_service import ProjectService

dashboard_bp = Blueprint('dashboard', __name__)
project_service = ProjectService()


@dashboard_bp.route('/')
@login_required
def index():
    stats = project_service.get_stats(current_user.id)
    recent_projects = project_service.get_user_projects(current_user.id)[:5]
    return render_template('dashboard/index.html', stats=stats, recent_projects=recent_projects)
