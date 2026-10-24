#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import jsonschema
import pytest
import yaml


MANIFEST_PATH = Path(__file__).resolve().parent.parent / "source_looker" / "manifest.yaml"


def _load_users_schema() -> dict:
    with open(MANIFEST_PATH) as f:
        manifest = yaml.safe_load(f)
    return manifest["schemas"]["users"]


EXPECTED_FIELDS = {
    "allow_direct_roles": "boolean",
    "allow_normal_group_membership": "boolean",
    "allow_roles_from_normal_groups": "boolean",
    "avatar_url": "string",
    "avatar_url_without_sizing": "string",
    "can": "object",
    "display_name": "string",
    "email": "string",
    "embed_group_folder_id": "string",
    "embed_group_space_id": "string",
    "first_name": "string",
    "group_ids": "array",
    "home_folder_id": "string",
    "id": "string",
    "is_disabled": "boolean",
    "last_name": "string",
    "locale": "string",
    "looker_versions": "array",
    "models_dir_validated": "boolean",
    "personal_folder_id": "string",
    "presumed_looker_employee": "boolean",
    "role_ids": "array",
    "roles_externally_managed": "boolean",
    "url": "string",
    "verified_looker_employee": "boolean",
}


def test_users_schema_contains_all_expected_fields():
    """Verify the users schema declares every field from the Looker API."""
    schema = _load_users_schema()
    properties = schema["properties"]
    for field_name, expected_type in EXPECTED_FIELDS.items():
        assert field_name in properties, f"Missing field: {field_name}"
        field_type = properties[field_name]["type"]
        assert expected_type in field_type, f"Field '{field_name}' should include type '{expected_type}', got {field_type}"
        assert "null" in field_type, f"Field '{field_name}' should be nullable"


def test_users_schema_allows_additional_properties():
    """Ensure additionalProperties is true so unknown fields pass through."""
    schema = _load_users_schema()
    assert schema.get("additionalProperties") is True


@pytest.mark.parametrize(
    "record",
    [
        pytest.param(
            {
                "id": "42",
                "email": "admin@example.com",
                "first_name": "Ada",
                "last_name": "Lovelace",
                "display_name": "Ada Lovelace",
                "is_disabled": False,
                "locale": "en",
                "role_ids": ["1", "2"],
                "group_ids": ["10"],
                "home_folder_id": "100",
                "personal_folder_id": "200",
                "avatar_url": "https://example.com/avatar.png",
                "avatar_url_without_sizing": "https://example.com/avatar_raw.png",
                "verified_looker_employee": False,
                "roles_externally_managed": False,
                "allow_direct_roles": True,
                "allow_normal_group_membership": True,
                "allow_roles_from_normal_groups": True,
                "embed_group_folder_id": None,
                "embed_group_space_id": None,
                "can": {"show": True, "index": True},
                "url": "https://looker.example.com/api/4.0/users/42",
                "looker_versions": ["24.0"],
                "models_dir_validated": True,
                "presumed_looker_employee": False,
            },
            id="full_user_record",
        ),
        pytest.param(
            {
                "id": "99",
                "email": None,
                "first_name": None,
                "last_name": None,
                "display_name": None,
                "is_disabled": None,
                "locale": None,
                "role_ids": None,
                "group_ids": None,
                "home_folder_id": None,
                "personal_folder_id": None,
                "avatar_url": None,
                "avatar_url_without_sizing": None,
                "verified_looker_employee": None,
                "roles_externally_managed": None,
                "allow_direct_roles": None,
                "allow_normal_group_membership": None,
                "allow_roles_from_normal_groups": None,
                "embed_group_folder_id": None,
                "embed_group_space_id": None,
                "can": None,
                "url": None,
                "looker_versions": None,
                "models_dir_validated": None,
                "presumed_looker_employee": None,
            },
            id="all_nullable_fields",
        ),
        pytest.param(
            {"id": "1", "email": "user@test.com", "url": "/api/4.0/users/1"},
            id="minimal_record_original_fields_only",
        ),
        pytest.param(
            {
                "id": "5",
                "email": "embed@test.com",
                "some_future_field": "should pass through",
            },
            id="record_with_unknown_additional_property",
        ),
    ],
)
def test_users_schema_validates_api_response(record):
    """Validate sample Looker API response records against the users schema."""
    schema = _load_users_schema()
    jsonschema.validate(instance=record, schema=schema)
