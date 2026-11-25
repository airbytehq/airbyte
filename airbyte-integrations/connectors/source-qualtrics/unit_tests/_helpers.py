# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared helpers for `source-qualtrics` unit tests."""

from pathlib import Path
from urllib.parse import parse_qs, urlparse

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


DATACENTER = "iad1"
BASE_URL = f"https://{DATACENTER}.qualtrics.com/API/v3"
TOKEN_URL = f"https://{DATACENTER}.qualtrics.com/oauth2/token"
SURVEYS_URL = f"{BASE_URL}/surveys"

TOKEN_PATH = "/oauth2/token"
SURVEYS_PATH = "/API/v3/surveys"

ACCESS_TOKEN = "test-access-token"
TOKEN_RESPONSE = {"access_token": ACCESS_TOKEN, "token_type": "Bearer", "expires_in": 3599, "scope": "read:surveys read:survey_responses"}
DEFAULT_SCOPE = "read:surveys read:survey_responses"

OAUTH_CONFIG = {
    "datacenter": DATACENTER,
    "credentials": {"auth_type": "client_credentials", "client_id": "test_client_id", "client_secret": "test_client_secret"},
}
API_TOKEN_CONFIG = {
    "datacenter": DATACENTER,
    "credentials": {"auth_type": "api_token", "api_token": "test-api-token"},
}


def _get_manifest_path() -> Path:
    """Resolve the directory holding the connector's `manifest.yaml`.

    In CI the connector is copied into `/airbyte/integration_code/source_declarative_manifest/`.
    Locally, tests run from the connector's `unit_tests/` directory, so the manifest lives
    one directory up.
    """
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"


def get_source(config: dict, state=None) -> YamlDeclarativeSource:
    """Instantiate a `YamlDeclarativeSource` for `source-qualtrics` using its manifest."""
    catalog = CatalogBuilder().build()
    state = state if state is not None else StateBuilder().build()
    return YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)


def read_stream(stream_name: str, config: dict = OAUTH_CONFIG, sync_mode: SyncMode = SyncMode.full_refresh) -> EntrypointOutput:
    """Run the connector against a single stream."""
    source = get_source(config=config, state=[])
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(source, config, catalog, [])


def stream_schema(stream_name: str, config: dict = OAUTH_CONFIG) -> dict:
    """The JSON schema the connector declares for a stream."""
    return next(stream for stream in get_source(config).streams(config) if stream.name == stream_name).get_json_schema()


def survey(survey_id: str, name: str = "Survey") -> dict:
    """One element of the `GET /surveys` list."""
    return {
        "id": survey_id,
        "name": name,
        "ownerId": "UR_owner",
        "lastModified": "2026-10-01T12:00:00Z",
        "creationDate": "2026-01-01T12:00:00Z",
        "isActive": True,
    }


def surveys_page(elements: list, next_page=None) -> dict:
    """Qualtrics' list envelope: `result.elements` and a full `result.nextPage` URL."""
    return {"result": {"elements": elements, "nextPage": next_page}, "meta": {"httpStatus": "200 - OK", "requestId": "req"}}


def survey_detail(survey_id: str) -> dict:
    """The `result` of `GET /surveys/{id}`, trimmed to the fields the connector types."""
    return {
        "result": {
            "id": survey_id,
            "name": "Survey",
            "ownerId": "UR_owner",
            "organizationId": "org",
            "isActive": True,
            "creationDate": "2026-01-01T12:00:00Z",
            "lastModifiedDate": "2026-10-01T12:00:00Z",
            "expiration": {"startDate": None, "endDate": None},
            "questions": {"QID1": {"questionType": {"type": "MC"}, "questionText": "How are you?"}},
            "exportColumnMap": {"Q1": {"question": "QID1"}},
            "blocks": {},
            "flow": [{"type": "Block", "id": "BL_1"}],
            "embeddedData": [],
            "comments": {},
            "loopAndMerge": {},
            "responseCounts": {"auditable": 3, "generated": 0, "deleted": 0},
        },
        "meta": {"httpStatus": "200 - OK", "requestId": "req"},
    }


def response_schema(survey_id: str) -> dict:
    """The `result` of `GET /surveys/{id}/response-schema`: a JSON Schema document."""
    return {
        "result": {
            "$schema": "https://json-schema.org/draft/2019-09/schema",
            "$id": f"http://qualtrics.com/API/v3/surveys/{survey_id}/response-schema",
            "title": "Survey",
            "description": "A response to the survey",
            "type": "object",
            "required": ["values", "displayedFields", "displayedValues", "labels", "responseId"],
            "properties": {"responseId": {"type": "string"}, "values": {"type": "object", "properties": {}}},
        },
        "meta": {"httpStatus": "200 - OK", "requestId": "req"},
    }


def query_params(request) -> dict:
    """Return the query parameters of a recorded request, preserving case."""
    return {key: values[0] for key, values in parse_qs(urlparse(request.url).query).items()}


def requests_to(request_history, path: str) -> list:
    """Filter recorded requests down to the ones targeting `path` (requests_mock lowercases paths)."""
    return [request for request in request_history if request.path.lower() == path.lower()]


def record_ids(output: EntrypointOutput, key: str = "id") -> list:
    """Return `key` of every record emitted by a read."""
    return [message.record.data[key] for message in output.records]
