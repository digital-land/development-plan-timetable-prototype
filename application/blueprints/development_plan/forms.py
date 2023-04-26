from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Optional


class PlanForm(FlaskForm):
    reference = StringField("Reference", validators=[DataRequired()])
    name = StringField("Name of plan", validators=[DataRequired()])
    organisations = StringField("Organisation", validators=[DataRequired()])
    description = TextAreaField("Brief description of plan", validators=[Optional()])
    development_plan_type = RadioField("Plan type", validators=[DataRequired()])
    period_start_date = StringField(
        "Plan start date",
        validators=[Optional()],
        description="The year the plan starts, for example, 2022",
    )
    period_end_date = StringField(
        "Plan end date",
        validators=[Optional()],
        description="The year the plan ends, for example, 2045",
    )
    documentation_url = StringField(
        "URL for plan information",
        validators=[Optional()],
    )


class EventForm(FlaskForm):
    development_plan_event = SelectField(
        "Development plan event", validators=[DataRequired()]
    )
    organisations = StringField("Organisation", validators=[DataRequired()])
    event_date_year = StringField("Event date year", validators=[Optional()])
    event_date_month = StringField("Event date month", validators=[Optional()])
    event_date_day = StringField("Event date day", validators=[Optional()])


class DocumentForm(FlaskForm):
    name = StringField("Name of supporting document", validators=[DataRequired()])
    description = TextAreaField("Brief description of supporting document")
    document_type = RadioField("Document type", validators=[DataRequired()])
    documentation_url = StringField(
        "URL for document information", validators=[Optional()]
    )
    document_url = StringField("Document URL", validators=[Optional()])
    organisations = StringField("Organisation", validators=[DataRequired()])
