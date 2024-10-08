import csv
import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_serializer, model_validator

from application.models import (
    DevelopmentPlan,
    DevelopmentPlanBoundary,
    DevelopmentPlanDocument,
    DevelopmentPlanTimetable,
)


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


class DevelopmentPlanBaseModel(DateModel):
    reference: str
    name: Optional[str] = None

    @model_validator(mode="after")
    def replace_none_with_empty_string(cls, values):
        for field in [
            "name",
        ]:
            if getattr(values, field) is None:
                setattr(values, field, "")
        return values


class DevelopmentPlanModel(DevelopmentPlanBaseModel):
    description: Optional[str] = None
    development_plan_type: str
    period_start_date: Optional[int]
    period_end_date: Optional[int]
    development_plan_type: str
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


class DevelopmentPlanTimetableModel(DevelopmentPlanBaseModel):
    development_plan: str
    development_plan_event: Optional[str] = None
    notes: Optional[str] = None
    event_date: str
    organisations: Optional[List[OrganisationModel]]

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

    @model_validator(mode="after")
    def replace_none_with_empty_string(cls, values):
        for field in [
            "notes",
            "development_plan_event",
        ]:
            if getattr(values, field) is None:
                setattr(values, field, "")
        return values


class DevelopementPlanDocumentModel(DevelopmentPlanBaseModel):
    development_plan: str
    document_type: str
    document_url: str
    documentation_url: str
    notes: Optional[str] = None
    description: Optional[str] = None

    organisations: Optional[List[OrganisationModel]]

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

    @model_validator(mode="after")
    def replace_none_with_empty_string(cls, values):
        for field in [
            "notes",
            "description",
        ]:
            if getattr(values, field) is None:
                setattr(values, field, "")
        return values


class DevelopmentPlanBoundaryModel(DevelopmentPlanBaseModel):
    geometry: str
    development_plan_boundary_type: str


def export_data_to_file():
    tempdir = TemporaryDirectory()
    path = Path(tempdir.name)
    for file, model in download_file_map.items():
        csv_path = path / file
        with open(csv_path, "w") as f:
            serializer_class = model_map[model]
            fieldnames = list(serializer_class.__fields__.keys())
            fieldnames = [field.replace("_", "-") for field in fieldnames]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for obj in model.query.all():
                serializer_class = model_map[model]
                m = serializer_class.model_validate(obj)
                data = m.model_dump(by_alias=True)
                writer.writerow(data)
    return tempdir


download_file_map = {
    "development-plan.csv": DevelopmentPlan,
    "development-plan-timetable.csv": DevelopmentPlanTimetable,
    "development-plan-document.csv": DevelopmentPlanDocument,
    "development-plan-boundary.csv": DevelopmentPlanBoundary,
}

model_map = {
    DevelopmentPlan: DevelopmentPlanModel,
    DevelopmentPlanTimetable: DevelopmentPlanTimetableModel,
    DevelopmentPlanDocument: DevelopementPlanDocumentModel,
    DevelopmentPlanBoundary: DevelopmentPlanBoundaryModel,
}
