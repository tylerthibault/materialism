from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.models.material_item import UnitType


class MaterialListForm(FlaskForm):
    name = StringField('List Name', validators=[DataRequired()])
    submit = SubmitField('Add List')


class MaterialItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired()], default=1)
    unit = SelectField('Unit', choices=[(u.value, u.value.title()) for u in UnitType],
                       default=UnitType.EACH.value)
    submit = SubmitField('Add Item')
