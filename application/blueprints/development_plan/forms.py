from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired


class PlanForm(FlaskForm):
    reference = StringField("Reference", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    # organisations = SelectMultipleField(
    #     "Organisation", validators=[DataRequired()], validate_choice=False
    # )
    organisations = StringField("Organisation", validators=[DataRequired()])
    description = TextAreaField("Description")
    notes = TextAreaField("Notes")
    development_plan_type = SelectField("Plan type", validators=[DataRequired()])
    period_start_date = StringField(
        "Plan start date",
        validators=[DataRequired()],
        description="The year the plan starts, for example, 2022",
    )
    period_end_date = StringField(
        "Plan end date",
        validators=[DataRequired()],
        description="The year the plan ends, for example, 2045",
    )
    documentation_url = StringField("URL", validators=[DataRequired()])


class EventForm(FlaskForm):
    development_plan_event = SelectField(
        "Development plan event", validators=[DataRequired()]
    )
    # organisations = SelectField("Organisation", validators=[DataRequired()])
    organisations = StringField("Organisation", validators=[DataRequired()])
    event_date_year = StringField("Event date year", validators=[DataRequired()])
    event_date_month = StringField("Event date month", validators=[DataRequired()])
    event_date_day = StringField("Event date day", validators=[DataRequired()])
    notes = TextAreaField("Notes")


class DocumentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    document_type = SelectField("Document type", validators=[DataRequired()])
    documentation_url = StringField("Documentation URL", validators=[DataRequired()])
    document_url = StringField("Document URL", validators=[DataRequired()])
    organisations = StringField("Organisation", validators=[DataRequired()])
    # organisations = SelectField("Organisation", validators=[DataRequired()])
