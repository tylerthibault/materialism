from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.models.project import ProjectStatus


class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(max=200)])
    client_name = StringField('Client Name', validators=[Optional(), Length(max=150)])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    status = SelectField('Status', choices=[(s.value, s.value.title()) for s in ProjectStatus],
                         default=ProjectStatus.ACTIVE.value)
    submit = SubmitField('Save')
