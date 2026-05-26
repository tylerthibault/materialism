from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.extensions import db

profile_bp = Blueprint('profile', __name__)


class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    company_name = StringField('Company Name', validators=[Optional(), Length(max=150)])
    zip_code = StringField('Zip Code', validators=[Optional(), Length(max=10)])
    submit = SubmitField('Save Changes')


@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def edit():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.company_name = form.company_name.data
        current_user.zip_code = form.zip_code.data
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile.edit'))
    return render_template('profile/edit.html', form=form)
