import os
from flask import Flask
from .extensions import db, login_manager, migrate, csrf
from .config import config_map


def create_app(env=None):
    app = Flask(__name__)

    env = env or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config_map.get(env, config_map['development']))

    # Ensure instance/ directory exists (SQLite needs it)
    os.makedirs(app.instance_path, exist_ok=True)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Import models so migrate picks them up
    with app.app_context():
        from .models import user, project, material_list, material_item, store, price_result  # noqa

    # Register blueprints
    from .controllers.landing import landing_bp
    from .controllers.auth import auth_bp
    from .controllers.dashboard import dashboard_bp
    from .controllers.projects import projects_bp
    from .controllers.materials import materials_bp
    from .controllers.compare import compare_bp
    from .controllers.profile import profile_bp

    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(materials_bp)
    app.register_blueprint(compare_bp)
    app.register_blueprint(profile_bp, url_prefix='/profile')

    # Error handlers
    from flask import render_template

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
