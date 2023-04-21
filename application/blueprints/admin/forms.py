from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


class EventForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired()],
        description="Give the event a recognisable name, for example, Public consulation start",
    )
    # reference = StringField(
    #     "Reference",
    #     validators=[DataRequired()],
    #     description="Add a reference in kebab case format, for example, public-consultation-start",
    # )
    description = TextAreaField("Description")


class PlanTypeForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired()],
        description="Give the plan type a recognisable name, for example, Local plan",
    )
    # reference = StringField(
    #     "Reference",
    #     validators=[DataRequired()],
    #     description="Add a reference in kebab case format, for example, local-plan",
    # )
    description = TextAreaField("Description")


class DocumentTypeForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired()],
        description="Give the document type a recognisable name, e.g. 'Inspectors report' and we'll create a reference for it",  # noqa
    )

    # reference = StringField(
    #     "Reference",
    #     validators=[DataRequired()],
    #     description="Add a reference in kebab case format, for example, inspectors-report",
    # )
    description = TextAreaField("Description")
