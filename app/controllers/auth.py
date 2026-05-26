from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.auth_forms import LoginForm, RegisterForm
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = auth_service.login(form.email.data, form.password.data, form.remember_me.data)
        if user:
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        auth_service.register({
            'email': form.email.data,
            'name': form.name.data,
            'company_name': form.company_name.data,
            'password': form.password.data,
        })
        flash('Account created! Please sign in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    auth_service.logout()
    return redirect(url_for('landing.index'))
