# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(
    os.environ.get(
        "ASHBY_MANIFEST_PATH",
        Path(__file__).parents[1] / "manifest.yaml",
    )
)

DOCUMENTED_FIELDS = {
    "applications": ["openings"],
    "candidates": ["location"],
    "custom_fields": ["description", "isPrivate", "isRequired", "selectableValues"],
    "departments": ["createdAt", "externalName", "extraData", "updatedAt"],
    "interview_stages": ["interviewStageGroupId"],
    "jobs": ["author", "brandId", "closedAt", "compensation", "createdAt", "location", "openedAt", "openings", "updatedAt"],
    "job_postings": [
        "applicationDeadline",
        "applyLink",
        "compensationTierSummary",
        "shouldDisplayCompensationOnJobBoard",
        "status",
        "updatedAt",
        "workplaceType",
    ],
    "locations": ["externalName", "extraData", "parentLocationId", "type", "workplaceType"],
    "users": ["customFields", "globalRole", "isEnabled", "managerId", "updatedAt"],
    "offers": ["formDefinition", "offerStatus", "versions"],
    "interview_schedules": ["createdAt", "interviewEvents", "scheduledBy", "updatedAt"],
    "application_criteria_evaluations": [
        "id",
        "criterion",
        "status",
        "skipReason",
        "outcomeNumber",
        "evaluatedAt",
    ],
}

NESTED_FIELDS = {
    "applications": {
        "candidate": ["id", "name", "primaryEmailAddress", "primaryPhoneNumber"],
        "job": ["id", "title", "locationId", "departmentId"],
        "hiringTeam": ["userId", "firstName", "lastName", "email", "role"],
        "customFields": ["id", "isPrivate", "title", "valueLabel", "value"],
    },
    "candidates": {
        "primaryEmailAddress": ["value", "type", "isPrimary"],
        "emailAddresses": ["value", "type", "isPrimary"],
        "phoneNumbers": ["value", "type", "isPrimary"],
        "primaryPhoneNumber": ["value", "type", "isPrimary"],
        "socialLinks": ["type", "url"],
        "tags": ["id", "title", "isArchived"],
        "fileHandles": ["id", "name", "handle"],
        "resumeFileHandle": ["id", "name", "handle"],
        "customFields": ["id", "isPrivate", "title", "value", "valueLabel"],
    },
    "jobs": {
        "hiringTeam": ["userId", "firstName", "lastName", "email", "role"],
        "customFields": ["id", "isPrivate", "title", "value", "valueLabel"],
    },
    "offers": {
        "latestVersion": [
            "id",
            "startDate",
            "salary",
            "createdAt",
            "openingId",
            "customFields",
            "fileHandles",
            "author",
            "approvalStatus",
        ]
    },
    "feedback_form_definitions": {"formDefinition": ["sections"]},
    "locations": {"address": ["postalAddress"]},
    "job_postings": {"locationIds": ["primaryLocationId", "secondaryLocationIds"]},
    "application_criteria_evaluations": {
        "criterion": [
            "id",
            "title",
            "type",
            "prompt",
            "applicationFormDefinitionId",
            "applicationFormFieldPath",
        ]
    },
}


@pytest.fixture(scope="module")
def manifest():
    with MANIFEST_PATH.open() as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="module")
def schemas(manifest):
    return {stream["name"]: stream["schema_loader"]["schema"] for stream in manifest["streams"]}


@pytest.mark.parametrize(
    ("stream_name", "field_name"),
    [pytest.param(stream, field, id=f"{stream}-{field}") for stream, fields in DOCUMENTED_FIELDS.items() for field in fields],
)
def test_documented_fields_are_declared(schemas, stream_name, field_name):
    properties = schemas[stream_name]["properties"]
    assert field_name in properties
    assert properties[field_name]["type"][0] == "null"


@pytest.mark.parametrize(
    ("stream_name", "field_name", "child_fields"),
    [
        pytest.param(stream, field, children, id=f"{stream}-{field}")
        for stream, fields in NESTED_FIELDS.items()
        for field, children in fields.items()
    ],
)
def test_nested_documented_fields_are_expanded(schemas, stream_name, field_name, child_fields):
    field = schemas[stream_name]["properties"][field_name]
    nested = field["items"] if field["type"][-1] == "array" else field
    assert set(child_fields).issubset(nested["properties"])
