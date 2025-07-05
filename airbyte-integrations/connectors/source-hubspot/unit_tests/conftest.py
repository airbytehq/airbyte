#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys
from pathlib import Path

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

NUMBER_OF_PROPERTIES = 2000
OBJECTS_WITH_DYNAMIC_SCHEMA = [
    "calls",
    "company",
    "contact",
    "deal",
    "deal_split",
    "emails",
    "form",
    "goal_targets",
    "leads",
    "line_item",
    "meetings",
    "notes",
    "tasks",
    "product",
    "ticket",
]


@pytest.fixture(name="oauth_config")
def oauth_config_fixture():
    return {
        "start_date": "2021-10-10T00:00:00Z",
        "credentials": {
            "credentials_title": "OAuth Credentials",
            "redirect_uri": "https://airbyte.io",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
            "access_token": "test_access_token",
            "token_expires": "2021-05-30T06:00:00Z",
        },
    }


@pytest.fixture(name="config_invalid_client_id")
def config_invalid_client_id_fixture():
    return {
        "start_date": "2021-01-10T00:00:00Z",
        "credentials": {
            "credentials_title": "OAuth Credentials",
            "client_id": "invalid_client_id",
            "client_secret": "invalid_client_secret",
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        },
    }


@pytest.fixture(name="config")
def config_fixture():
    return {
        "start_date": "2021-01-10T00:00:00Z",
        "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
        "enable_experimental_streams": False,
    }


@pytest.fixture(name="config_experimental")
def config_eperimantal_fixture():
    return {
        "start_date": "2021-01-10T00:00:00Z",
        "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
        "enable_experimental_streams": True,
    }


@pytest.fixture(name="config_invalid_date")
def config_invalid_date_fixture():
    return {
        "start_date": "2000-00-00T00:00:00Z",
        "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
    }


@pytest.fixture(name="some_credentials")
def some_credentials_fixture():
    return {"credentials_title": "Private App Credentials", "access_token": "wrong token"}


@pytest.fixture(name="fake_properties_list")
def fake_properties_list():
    return [f"property_number_{i}" for i in range(NUMBER_OF_PROPERTIES)]


@pytest.fixture(name="migrated_properties_list")
def migrated_properties_list():
    return [
        "hs_v2_date_entered_prospect",
        "hs_v2_date_exited_prospect",
        "hs_v2_cumulative_time_in_prsopect",
        "hs_v2_some_other_property_in_prospect",
    ]


@pytest.fixture
def http_mocker():
    return None


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


def get_source(config, state=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def find_stream(stream_name, config, state=None):
    state = StateBuilder().build() if not state else state
    streams = get_source(config, state).streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


@pytest.fixture(autouse=True)
def patch_time(mocker):
    mocker.patch("time.sleep")


def read_from_stream(cfg, stream: str, sync_mode, state=None, expecting_exception: bool = False) -> EntrypointOutput:
    return read(get_source(cfg, state), cfg, CatalogBuilder().with_stream(stream, sync_mode).build(), state, expecting_exception)


@pytest.fixture()
def mock_dynamic_schema_requests(requests_mock):
    for entity in OBJECTS_WITH_DYNAMIC_SCHEMA:
        requests_mock.get(
            f"https://api.hubapi.com/properties/v2/{entity}/properties",
            json=[
                {
                    "name": "hs__migration_soft_delete",
                    "label": "migration_soft_delete_deprecated",
                    "description": "Describes if the goal target can be treated as deleted.",
                    "groupName": "goal_target_information",
                    "type": "enumeration",
                }
            ],
            status_code=200,
        )


def mock_dynamic_schema_requests_with_skip(requests_mock, object_to_skip: list):
    # Mock CustomObjects streams
    requests_mock.get(
        "https://api.hubapi.com/crm/v3/schemas",
        json={},
        status_code=200,
    )

    for object_name in OBJECTS_WITH_DYNAMIC_SCHEMA:
        if object_name in object_to_skip:
            continue
        requests_mock.get(
            f"https://api.hubapi.com/properties/v2/{object_name}/properties",
            json=[{"name": "hs__test_field", "type": "enumeration"}],
            status_code=200,
        )


@pytest.fixture(name="custom_object_schema")
def custom_object_schema_fixture():
    return {
        "labels": {"this": "that"},
        "requiredProperties": ["name"],
        "searchableProperties": ["name"],
        "primaryDisplayProperty": "name",
        "secondaryDisplayProperties": [],
        "archived": False,
        "restorable": True,
        "metaType": "PORTAL_SPECIFIC",
        "id": "7232155",
        "fullyQualifiedName": "p19936848_Animal",
        "createdAt": "2022-06-17T18:40:27.019Z",
        "updatedAt": "2022-06-17T18:40:27.019Z",
        "objectTypeId": "2-7232155",
        "properties": [
            {
                "name": "name",
                "label": "Animal name",
                "type": "string",
                "fieldType": "text",
                "description": "The animal name.",
                "groupName": "animal_information",
                "options": [],
                "displayOrder": -1,
                "calculated": False,
                "externalOptions": False,
                "hasUniqueValue": False,
                "hidden": False,
                "hubspotDefined": False,
                "modificationMetadata": {"archivable": True, "readOnlyDefinition": True, "readOnlyValue": False},
                "formField": True,
            }
        ],
        "associations": [],
        "name": "animals",
    }


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture():
    configured_catalog = {
        "streams": [
            {
                "stream": {
                    "name": "quotes",
                    "json_schema": {},
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["updatedAt"],
                },
                "sync_mode": "incremental",
                "cursor_field": ["updatedAt"],
                "destination_sync_mode": "append",
            }
        ]
    }
    return ConfiguredAirbyteCatalog.parse_obj(configured_catalog)


@pytest.fixture(name="expected_custom_object_json_schema")
def expected_custom_object_json_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": ["null", "object"],
        "additionalProperties": True,
        "properties": {
            "id": {"type": ["null", "string"]},
            "createdAt": {"type": ["null", "string"], "format": "date-time"},
            "updatedAt": {"type": ["null", "string"], "format": "date-time"},
            "archived": {"type": ["null", "boolean"]},
            "properties": {"type": ["null", "object"], "properties": {"name": {"type": ["null", "string"]}}},
            "properties_name": {"type": ["null", "string"]},
        },
    }
