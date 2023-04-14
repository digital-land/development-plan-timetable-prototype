from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


class PlanForm(FlaskForm):
    reference = StringField("Reference", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    organisation = StringField("Organisation", validators=[DataRequired()])
    description = TextAreaField("Description")
    development_plan_type = StringField("Plan type", validators=[DataRequired()])
    period_start_date = StringField("Plan start date", validators=[DataRequired()])
    period_end_date = StringField("Plan end date", validators=[DataRequired()])
    documentation_url = StringField("URL", validators=[DataRequired()])
