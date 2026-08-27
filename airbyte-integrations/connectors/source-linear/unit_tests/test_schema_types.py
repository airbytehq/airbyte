from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.yaml"

EXPECTED_FORMATS = {
    ("issues", "addedToCycleAt"): "date-time",
    ("issues", "addedToProjectAt"): "date-time",
    ("issues", "addedToTeamAt"): "date-time",
    ("issues", "archivedAt"): "date-time",
    ("issues", "canceledAt"): "date-time",
    ("issues", "completedAt"): "date-time",
    ("issues", "createdAt"): "date-time",
    ("issues", "dueDate"): "date",
    ("issues", "startedAt"): "date-time",
    ("issues", "updatedAt"): "date-time",
    ("customers", "archivedAt"): "date-time",
    ("customers", "createdAt"): "date-time",
    ("customers", "updatedAt"): "date-time",
    ("users", "archivedAt"): "date-time",
    ("users", "createdAt"): "date-time",
    ("users", "lastSeen"): "date-time",
    ("users", "updatedAt"): "date-time",
    ("comments", "archivedAt"): "date-time",
    ("comments", "createdAt"): "date-time",
    ("comments", "editedAt"): "date-time",
    ("comments", "updatedAt"): "date-time",
    ("cycles", "completedAt"): "date-time",
    ("cycles", "archivedAt"): "date-time",
    ("cycles", "createdAt"): "date-time",
    ("cycles", "endsAt"): "date-time",
    ("cycles", "startsAt"): "date-time",
    ("cycles", "updatedAt"): "date-time",
    ("customer_needs", "archivedAt"): "date-time",
    ("customer_needs", "createdAt"): "date-time",
    ("customer_needs", "updatedAt"): "date-time",
    ("projects", "archivedAt"): "date-time",
    ("projects", "canceledAt"): "date-time",
    ("projects", "completedAt"): "date-time",
    ("projects", "createdAt"): "date-time",
    ("projects", "healthUpdatedAt"): "date-time",
    ("projects", "startDate"): "date",
    ("projects", "startedAt"): "date-time",
    ("projects", "targetDate"): "date",
    ("projects", "updatedAt"): "date-time",
    ("project_milestones", "archivedAt"): "date-time",
    ("project_milestones", "createdAt"): "date-time",
    ("project_milestones", "targetDate"): "date",
    ("project_milestones", "updatedAt"): "date-time",
    ("project_statuses", "archivedAt"): "date-time",
    ("project_statuses", "createdAt"): "date-time",
    ("project_statuses", "updatedAt"): "date-time",
    ("issue_labels", "archivedAt"): "date-time",
    ("issue_labels", "createdAt"): "date-time",
    ("issue_labels", "updatedAt"): "date-time",
    ("workflow_states", "archivedAt"): "date-time",
    ("workflow_states", "createdAt"): "date-time",
    ("workflow_states", "updatedAt"): "date-time",
    ("teams", "archivedAt"): "date-time",
    ("teams", "createdAt"): "date-time",
    ("teams", "updatedAt"): "date-time",
    ("attachments", "archivedAt"): "date-time",
    ("attachments", "createdAt"): "date-time",
    ("attachments", "updatedAt"): "date-time",
    ("issue_relations", "archivedAt"): "date-time",
    ("issue_relations", "createdAt"): "date-time",
    ("issue_relations", "updatedAt"): "date-time",
    ("customer_statuses", "archivedAt"): "date-time",
    ("customer_statuses", "createdAt"): "date-time",
    ("customer_statuses", "updatedAt"): "date-time",
    ("customer_tiers", "archivedAt"): "date-time",
    ("customer_tiers", "createdAt"): "date-time",
    ("customer_tiers", "updatedAt"): "date-time",
    ("initiatives", "archivedAt"): "date-time",
    ("initiatives", "canceledAt"): "date-time",
    ("initiatives", "completedAt"): "date-time",
    ("initiatives", "createdAt"): "date-time",
    ("initiatives", "healthUpdatedAt"): "date-time",
    ("initiatives", "startedAt"): "date-time",
    ("initiatives", "targetDate"): "date",
    ("initiatives", "updatedAt"): "date-time",
    ("initiative_to_projects", "archivedAt"): "date-time",
    ("initiative_to_projects", "createdAt"): "date-time",
    ("initiative_to_projects", "updatedAt"): "date-time",
    ("project_updates", "archivedAt"): "date-time",
    ("project_updates", "createdAt"): "date-time",
    ("project_updates", "editedAt"): "date-time",
    ("project_updates", "updatedAt"): "date-time",
    ("issue_history", "archivedAt"): "date-time",
    ("issue_history", "createdAt"): "date-time",
    ("issue_history", "fromDueDate"): "date",
    ("issue_history", "toDueDate"): "date",
    ("issue_history", "updatedAt"): "date-time",
}

SETTLED_FORMATS = [
    ("attachments", "createdAt", "date-time"),
    ("attachments", "updatedAt", "date-time"),
    ("comments", "createdAt", "date-time"),
    ("comments", "editedAt", "date-time"),
    ("comments", "updatedAt", "date-time"),
    ("customer_needs", "createdAt", "date-time"),
    ("customer_needs", "updatedAt", "date-time"),
    ("customer_statuses", "createdAt", "date-time"),
    ("customer_statuses", "updatedAt", "date-time"),
    ("customer_tiers", "createdAt", "date-time"),
    ("customer_tiers", "updatedAt", "date-time"),
    ("customers", "createdAt", "date-time"),
    ("customers", "updatedAt", "date-time"),
    ("cycles", "completedAt", "date-time"),
    ("cycles", "createdAt", "date-time"),
    ("cycles", "endsAt", "date-time"),
    ("cycles", "startsAt", "date-time"),
    ("cycles", "updatedAt", "date-time"),
    ("issue_labels", "createdAt", "date-time"),
    ("issue_labels", "updatedAt", "date-time"),
    ("issue_relations", "createdAt", "date-time"),
    ("issue_relations", "updatedAt", "date-time"),
    ("issues", "addedToCycleAt", "date-time"),
    ("issues", "addedToProjectAt", "date-time"),
    ("issues", "addedToTeamAt", "date-time"),
    ("issues", "canceledAt", "date-time"),
    ("issues", "completedAt", "date-time"),
    ("issues", "createdAt", "date-time"),
    ("issues", "dueDate", "date"),
    ("issues", "startedAt", "date-time"),
    ("issues", "updatedAt", "date-time"),
    ("project_milestones", "createdAt", "date-time"),
    ("project_milestones", "targetDate", "date"),
    ("project_milestones", "updatedAt", "date-time"),
    ("project_statuses", "createdAt", "date-time"),
    ("project_statuses", "updatedAt", "date-time"),
    ("projects", "canceledAt", "date-time"),
    ("projects", "completedAt", "date-time"),
    ("projects", "createdAt", "date-time"),
    ("projects", "healthUpdatedAt", "date-time"),
    ("projects", "startDate", "date"),
    ("projects", "startedAt", "date-time"),
    ("projects", "targetDate", "date"),
    ("projects", "updatedAt", "date-time"),
    ("teams", "createdAt", "date-time"),
    ("teams", "updatedAt", "date-time"),
    ("users", "createdAt", "date-time"),
    ("users", "lastSeen", "date-time"),
    ("users", "updatedAt", "date-time"),
    ("workflow_states", "createdAt", "date-time"),
    ("workflow_states", "updatedAt", "date-time"),
]


@pytest.fixture
def manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())


@pytest.mark.parametrize(
    ("stream", "field", "expected_format"),
    SETTLED_FORMATS,
)
def test_settled_date_formats(
    manifest: dict, stream: str, field: str, expected_format: str
) -> None:
    assert manifest["schemas"][stream]["properties"][field]["format"] == expected_format


def test_all_date_formats_are_expected(manifest: dict) -> None:
    actual_formats = {
        (stream, field): property_schema["format"]
        for stream, schema in manifest["schemas"].items()
        for field, property_schema in schema["properties"].items()
        if property_schema.get("format") in {"date", "date-time"}
    }

    assert actual_formats == EXPECTED_FORMATS


def test_cycle_cooldown_time_is_a_duration(manifest: dict) -> None:
    assert "format" not in manifest["schemas"]["teams"]["properties"]["cycleCooldownTime"]


def test_deprecated_fields_are_removed_and_visibility_is_added(manifest: dict) -> None:
    users_query = manifest["definitions"]["streams"]["users"]["retriever"]["requester"][
        "request_body_json"
    ]["query"]
    teams_query = manifest["definitions"]["streams"]["teams"]["retriever"]["requester"][
        "request_body_json"
    ]["query"]
    customer_statuses_query = manifest["definitions"]["streams"]["customer_statuses"][
        "retriever"
    ]["requester"]["request_body_json"]["query"]

    assert "inviteHash" not in users_query
    assert "inviteHash" not in teams_query
    assert "private" not in teams_query
    assert " type " not in customer_statuses_query
    assert "visibility" in teams_query
    assert "inviteHash" not in manifest["schemas"]["users"]["properties"]
    assert "inviteHash" not in manifest["schemas"]["teams"]["properties"]
    assert "private" not in manifest["schemas"]["teams"]["properties"]
    assert manifest["schemas"]["teams"]["properties"]["visibility"]["type"] == [
        "string",
        "null",
    ]


def test_marked_as_duplicate_workflow_state_is_preserved(manifest: dict) -> None:
    teams = manifest["definitions"]["streams"]["teams"]
    teams_query = teams["retriever"]["requester"]["request_body_json"]["query"]

    assert "markedAsDuplicateWorkflowState" in teams_query
    assert any(
        field["path"] == ["markedAsDuplicateWorkflowStateId"]
        for transformation in teams["transformations"]
        if transformation["type"] == "AddFields"
        for field in transformation["fields"]
    )
