# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-livetennisapi`.

Everything here runs against a mocked HTTP layer, so the suite needs no
credentials and can run in CI. It covers the parts of the manifest that are
easy to get wrong and impossible to see from the YAML alone: the `X-API-Key`
authenticator, the `{data: [...], meta: {...}}` record envelope, offset
pagination, and the plan-tier error mapping — `completed_matches` is the one
stream that needs a paid BASIC key, and a free key gets `403 upgrade_required`
on it.
"""

from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"

_API_KEY = "test-api-key"
_CONFIG = {"api_key": _API_KEY}
_BASE_URL = "https://api.livetennisapi.com/api/public/v1"

_FREE_STREAMS = ["live_matches", "upcoming_matches", "players", "fixtures"]
_ALL_STREAMS = ["live_matches", "upcoming_matches", "completed_matches", "players", "fixtures"]

# Endpoint each stream reads, and the `status` filter it sends (None = no filter).
_STREAM_ENDPOINTS = {
    "live_matches": ("matches", "live"),
    "upcoming_matches": ("matches", "upcoming"),
    "completed_matches": ("matches", "completed"),
    "players": ("players", None),
    "fixtures": ("fixtures", None),
}


def _get_source(config=None) -> YamlDeclarativeSource:
    config = config or _CONFIG
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=StateBuilder().build(),
    )


def _sync(stream_name, config=None):
    config = config or _CONFIG
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(_get_source(config), config, catalog)


def _sync_expecting_failure(stream_name, config=None):
    config = config or _CONFIG
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(_get_source(config), config, catalog, expecting_exception=True)


def _envelope(records, limit=200, offset=0):
    return {"data": records, "meta": {"limit": limit, "offset": offset, "count": len(records)}}


def _match(match_id, **overrides):
    record = {
        "id": match_id,
        "tournament": "Australian Open",
        "tournament_id": 100,
        "tour": "atp",
        "round": "R16",
        "player1": "A Player",
        "player2": "B Player",
        "player1_id": 1,
        "player2_id": 2,
        "status": "live",
        "start_time": "2026-01-20T04:00:00Z",
    }
    record.update(overrides)
    return record


def _player(player_id, **overrides):
    record = {"id": player_id, "name": "A Player", "country": "ESP", "tour": "atp", "ranking": 1}
    record.update(overrides)
    return record


def _fixture(fixture_id, **overrides):
    record = {"id": fixture_id, "tournament": "Australian Open", "tour": "atp", "start_time": "2026-01-21T04:00:00Z"}
    record.update(overrides)
    return record


def _record_for(stream_name, record_id):
    if stream_name == "players":
        return _player(record_id)
    if stream_name == "fixtures":
        return _fixture(record_id)
    return _match(record_id)


# --- discovery -------------------------------------------------------------


def _discovered_streams():
    output = discover(_get_source(), _CONFIG)
    return {stream.name: stream for stream in output.catalog.catalog.streams}


def test_all_streams_are_discoverable():
    assert sorted(_discovered_streams()) == sorted(_ALL_STREAMS)


@pytest.mark.parametrize("stream_name", _ALL_STREAMS)
def test_every_stream_has_id_as_primary_key(stream_name):
    stream = _discovered_streams()[stream_name]
    assert stream.source_defined_primary_key == [["id"]]


@pytest.mark.parametrize("stream_name", _ALL_STREAMS)
def test_every_stream_is_full_refresh_only(stream_name):
    """The API exposes no cursor, so nothing here may advertise incremental."""
    stream = _discovered_streams()[stream_name]
    assert [mode.value for mode in stream.supported_sync_modes] == ["full_refresh"]


# --- authentication --------------------------------------------------------


@pytest.mark.parametrize("stream_name", _ALL_STREAMS)
def test_api_key_is_sent_as_the_x_api_key_header(stream_name):
    endpoint, _ = _STREAM_ENDPOINTS[stream_name]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/{endpoint}", json=_envelope([]))
        _sync(stream_name)

    assert mocker.last_request.headers["X-API-Key"] == _API_KEY


def test_api_key_is_never_put_in_the_query_string():
    """The key is a header credential; it must not leak into a URL that ends up in logs."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/players", json=_envelope([]))
        _sync("players")

    assert _API_KEY not in mocker.last_request.url


# --- records and request shape ---------------------------------------------


@pytest.mark.parametrize("stream_name", _ALL_STREAMS)
def test_records_are_read_from_the_data_envelope(stream_name):
    endpoint, _ = _STREAM_ENDPOINTS[stream_name]
    payload = _envelope([_record_for(stream_name, 1), _record_for(stream_name, 2)])

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/{endpoint}", json=payload)
        output = _sync(stream_name)

    assert [r.record.data["id"] for r in output.records] == [1, 2]


@pytest.mark.parametrize("stream_name", _ALL_STREAMS)
def test_stream_requests_the_right_endpoint_and_status_filter(stream_name):
    endpoint, status = _STREAM_ENDPOINTS[stream_name]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/{endpoint}", json=_envelope([]))
        _sync(stream_name)

    assert mocker.last_request.path.endswith(f"/{endpoint}")
    if status is None:
        assert "status" not in mocker.last_request.qs
    else:
        assert mocker.last_request.qs["status"] == [status]


def test_empty_response_emits_no_records():
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/matches", json=_envelope([]))
        output = _sync("live_matches")

    assert output.records == []


# --- pagination ------------------------------------------------------------


def test_first_page_asks_for_the_documented_maximum_page_size():
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/players", json=_envelope([]))
        _sync("players")

    assert mocker.last_request.qs["limit"] == ["200"]


def test_offset_pagination_walks_pages_and_stops_on_a_short_page():
    full_page = [_player(i) for i in range(1, 201)]
    short_page = [_player(201)]

    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/players",
            [
                {"json": _envelope(full_page, offset=0), "status_code": 200},
                {"json": _envelope(short_page, offset=200), "status_code": 200},
            ],
        )
        output = _sync("players")
        offsets = [request.qs.get("offset", ["0"])[0] for request in mocker.request_history]

    assert len(output.records) == 201
    assert offsets == ["0", "200"], "expected exactly two pages: offset 0, then offset 200"


# --- plan tiers and error mapping ------------------------------------------


def test_401_is_reported_as_a_config_error():
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/players", status_code=401, json={"error": "unauthorized"})
        output = _sync_expecting_failure("players")

    assert output.records == []
    messages = [trace.trace.error.message for trace in output.trace_messages if trace.trace.error]
    assert any("401" in message for message in messages)


def test_completed_matches_403_is_a_config_error_that_names_the_paid_tier():
    """A free key gets `403 upgrade_required` on `status=completed`.

    The message must tell the user which stream and which plan, because
    otherwise it reads as "your key is broken" when the key is fine.
    """
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/matches", status_code=403, json={"error": "upgrade_required"})
        output = _sync_expecting_failure("completed_matches")

    assert output.records == []
    messages = [trace.trace.error.message for trace in output.trace_messages if trace.trace.error]
    assert messages, "a 403 must surface an error trace, not an empty successful sync"
    joined = " ".join(messages)
    assert "completed_matches" in joined
    assert "BASIC" in joined


def test_the_403_message_does_not_claim_every_stream_is_free():
    """Regression guard: an earlier revision told free-tier users their key was
    downgraded when they hit the one stream that genuinely needs a paid plan."""
    filters = _manifest_response_filters()
    message = next(f["error_message"] for f in filters if 403 in f["http_codes"])
    assert "Every stream in this" not in message


@pytest.mark.parametrize("stream_name", _FREE_STREAMS)
def test_free_tier_streams_sync_on_a_free_key(stream_name):
    endpoint, _ = _STREAM_ENDPOINTS[stream_name]

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/{endpoint}", json=_envelope([_record_for(stream_name, 1)]))
        output = _sync(stream_name)

    assert len(output.records) == 1


def test_429_is_retried_after_the_retry_after_header():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/players",
            [
                {"status_code": 429, "headers": {"Retry-After": "0"}, "json": {"error": "rate_limited"}},
                {"status_code": 200, "json": _envelope([_player(1)])},
            ],
        )
        output = _sync("players")

    assert len(output.records) == 1
    assert len(mocker.request_history) == 2


# --- spec ------------------------------------------------------------------


def _manifest():
    import yaml

    with open(_MANIFEST_PATH) as manifest_file:
        return yaml.safe_load(manifest_file)


def _manifest_response_filters():
    return _manifest()["definitions"]["base_requester"]["error_handler"]["response_filters"]


def test_spec_documents_that_completed_matches_needs_a_paid_key():
    """The spec text is the only place a user sees plan tiers before they sync."""
    description = _manifest()["spec"]["connection_specification"]["properties"]["api_key"]["description"]
    assert "completed_matches" in description
    assert "BASIC" in description


def test_api_key_is_marked_as_a_secret():
    api_key = _manifest()["spec"]["connection_specification"]["properties"]["api_key"]
    assert api_key["airbyte_secret"] is True
