# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from requests import Request

from airbyte_cdk.test.entrypoint_wrapper import discover
from unit_tests.conftest import get_source
from unit_tests.integration.zoom_mocks import CONFIG, assert_records_match_schema


_CI_MANIFEST_DIR = Path("/airbyte/integration_code/source_declarative_manifest")
_MANIFEST_DIR = _CI_MANIFEST_DIR if _CI_MANIFEST_DIR.exists() else Path(__file__).parent.parent
_MANIFEST_PATH = _MANIFEST_DIR / "manifest.yaml"
_METADATA_PATH = _MANIFEST_DIR / "metadata.yaml"
_TOKEN_URL = "https://zoom.us/oauth/token"

EXPECTED_PRIMARY_KEYS = {
    "users": [["id"]],
    "meetings": [["id"]],
    "meeting_registrants": [["id"]],
    "meeting_polls": [["meeting_id"], ["id"]],
    "meeting_poll_results": None,
    "meeting_registration_questions": [["meeting_id"]],
    "webinars": [["id"]],
    "webinar_panelists": [["webinar_id"], ["id"]],
    "webinar_registrants": [["webinar_id"], ["id"]],
    "webinar_absentees": [["id"]],
    "webinar_polls": [["webinar_id"], ["id"]],
    "webinar_poll_results": None,
    "webinar_registration_questions": [["webinar_id"]],
    "webinar_tracking_sources": [["id"]],
    "webinar_qna_results": None,
    "report_meetings": [["uuid"]],
    "report_meeting_participants": [["meeting_uuid"], ["user_id"]],
    "report_webinars": [["uuid"]],
    "report_webinar_participants": [["webinar_uuid"], ["user_id"]],
    "report_user_meetings": [["uuid"]],
    "report_daily": [["date"]],
    "chat_channels": [["id"], ["user_id"]],
    "zoom_events": [["event_id"]],
}


def _manifest_streams():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    for stream_entry in manifest["streams"]:
        stream = stream_entry
        if "$ref" in stream_entry:
            stream = manifest
            for path_segment in stream_entry["$ref"].removeprefix("#/").split("/"):
                stream = stream[path_segment]
        yield stream


@pytest.fixture(scope="module")
def discovered_streams():
    catalog = discover(get_source(config=CONFIG), CONFIG).catalog.catalog
    return {stream.name: stream for stream in catalog.streams}


def test_discovery_primary_keys_match_expected_contract(discovered_streams):
    assert set(discovered_streams) == set(EXPECTED_PRIMARY_KEYS)
    for stream_name, expected_primary_key in EXPECTED_PRIMARY_KEYS.items():
        assert discovered_streams[stream_name].source_defined_primary_key == expected_primary_key


@pytest.mark.parametrize(
    "stream_name",
    [
        "webinar_panelists",
        "webinar_registrants",
        "webinar_polls",
        "webinar_registration_questions",
        "webinar_poll_results",
        "webinar_qna_results",
        "webinar_tracking_sources",
    ],
)
def test_discovery_webinar_id_is_integer(discovered_streams, stream_name):
    assert discovered_streams[stream_name].json_schema["properties"]["webinar_id"]["type"] == ["null", "integer"]


@pytest.mark.parametrize("timestamp", [pytest.param("not-a-date", id="invalid-date-time")])
def test_schema_validation_rejects_invalid_date_time(timestamp):
    output = SimpleNamespace(records=[SimpleNamespace(record=SimpleNamespace(data={"end_time": timestamp}))])

    with pytest.raises(AssertionError):
        assert_records_match_schema(output, "report_user_meetings")


def test_connection_spec_has_titled_fields_and_optional_hidden_authorization_endpoint():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    specification = manifest["spec"]["connection_specification"]
    properties = specification["properties"]

    assert all(property_spec.get("title") for property_spec in properties.values())
    credentials_options = properties["credentials"]["oneOf"]
    for option in credentials_options:
        assert all(property_spec.get("title") for property_spec in option["properties"].values())

    server_to_server = next(
        (option for option in credentials_options if option["properties"]["auth_type"].get("const") == "server_to_server"),
        None,
    )
    assert server_to_server is not None
    assert "authorization_endpoint" not in server_to_server.get("required", [])
    authorization_endpoint = server_to_server["properties"]["authorization_endpoint"]
    assert authorization_endpoint["airbyte_hidden"] is True
    assert authorization_endpoint["default"] == _TOKEN_URL


def test_num_workers_is_optional_with_concurrency_bounds():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    specification = manifest["spec"]["connection_specification"]
    num_workers = specification["properties"]["num_workers"]

    assert num_workers["type"] == "integer"
    assert num_workers["title"] == "Number of Concurrent Threads"
    assert num_workers["default"] == 3
    assert num_workers["minimum"] == 2
    assert num_workers["maximum"] == 10
    assert "num_workers" not in specification.get("required", [])

    concurrency_level = manifest["concurrency_level"]
    assert concurrency_level["default_concurrency"] == "{{ config.get('num_workers', 3) }}"
    assert concurrency_level["max_concurrency"] == 10


@pytest.fixture(scope="module")
def source_api_budget():
    source = get_source(config=CONFIG)
    first_stream = source.streams(CONFIG)[0]
    retriever = first_stream._stream_partition_generator._partition_factory._retriever
    return retriever.requester.api_budget


@pytest.mark.parametrize(
    "path, expected_limit",
    [
        ("/v2/report/meetings/abc%252Fdef%253D%253D/participants", 10),
        ("/v2/report/meetings/123", 10),
        ("/v2/report/daily", 10),
        ("/v2/report/users/u1/meetings", 10),
        ("/v2/past_webinars/x/absentees", 10),
        ("/v2/users", 20),
        ("/v2/users/u1/meetings", 20),
        ("/v2/users/u1/webinars", 20),
        ("/v2/meetings/1/registrants", 20),
        ("/v2/webinars/1/panelists", 20),
        ("/v2/webinars/1/tracking_sources", 20),
        ("/v2/past_meetings/x/polls", 20),
        ("/v2/past_webinars/x/qa", 20),
        ("/v2/chat/users/u1/channels", 20),
        ("/v2/meetings/1", 30),
        ("/v2/meetings/1/polls", 30),
        ("/v2/meetings/1/registrants/questions", 30),
        ("/v2/webinars/1", 30),
        ("/v2/zoom_events/events", 30),
    ],
)
def test_api_budget_routes_requests_by_zoom_category(source_api_budget, path, expected_limit):
    request = Request("GET", f"https://api.zoom.us{path}").prepare()
    matching_policies = [policy for policy in source_api_budget._policies if policy.matches(request)]

    assert matching_policies
    assert source_api_budget.get_matching_policy(request) is matching_policies[0]
    assert matching_policies[0]._bucket.rates[0].limit == expected_limit


def test_metadata_has_registry_hosts_heartbeat_and_suggested_streams():
    if not _METADATA_PATH.exists():
        pytest.skip("metadata.yaml is not available next to manifest.yaml")

    metadata = yaml.safe_load(_METADATA_PATH.read_text())["data"]
    suggested_streams = [
        "users",
        "meetings",
        "meeting_registrants",
        "report_meetings",
        "report_meeting_participants",
    ]

    assert metadata["allowedHosts"]["hosts"] == ["api.zoom.us", "zoom.us"]
    assert metadata["maxSecondsBetweenMessages"] == 5400
    assert metadata["suggestedStreams"]["streams"] == suggested_streams

    manifest_stream_names = {stream["name"] for stream in _manifest_streams()}
    assert set(suggested_streams).issubset(manifest_stream_names)
