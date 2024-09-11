import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_serializer, model_validator


class OrganisationModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=lambda x: x.replace("_", "-"),
        populate_by_name=True,
    )

    organisation: str


class DateModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=lambda x: x.replace("_", "-"),
        populate_by_name=True,
    )

    entry_date: Optional[datetime.date]
    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]

    @field_serializer(
        "entry_date",
        "start_date",
        "end_date",
    )
    def serialize_date(self, value):
        if value is not None:
            return value.strftime("%Y-%m-%d")
        return ""


class DevelopmentPlanModel(DateModel):
    reference: str
    name: str
    description: Optional[str] = None
    development_plan_type: str
    period_start_date: Optional[int]
    period_end_date: Optional[int]
    development_plan_boundary: Optional[str] = None
    documentation_url: Optional[str] = None
    adopted_date: Optional[str] = None
    organisations: Optional[List[OrganisationModel]]

    @model_validator(mode="after")
    def replace_none_with_empty_string(cls, values):
        for field in [
            "description",
            "development_plan_boundary",
            "documentation_url",
            "adopted_date",
        ]:
            if getattr(values, field) is None:
                setattr(values, field, "")
        return values

    @field_serializer(
        "organisations",
    )
    def serialize_organisations(self, value):
        orgs = []
        if value is not None:
            for val in value:
                orgs.append(val.organisation)
        if orgs:
            return ";".join(orgs)
        return ""
