#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Coverage for streams bypassed in `acceptance-test-config.yml` via `empty_streams`.

`goals`, `leads`, and `workflows` back onto HubSpot objects that need paid product access
(Sales Hub Enterprise, Sales Hub Professional, and automation respectively). The CI test portal
lost those entitlements, so the live acceptance read returns 403 and yields no records. These
tests keep the behaviour that `basic_read` used to assert: records come through, they match the
declared schema, incremental runs emit state, and an empty page is not treated as a failure.
"""

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover

from .conftest import find_stream, get_source, mock_dynamic_schema_requests_with_skip, read_from_stream


# stream name -> (properties entity used for dynamic schemas, one API record shaped like the
# stream's declared schema; `workflows` carries an epoch-millis cursor rather than an ISO string)
GATED_STREAMS = {
    "goals": (
        "goal_targets",
        {
            "id": "test_id",
            "createdAt": "2022-02-25T16:43:11Z",
            "updatedAt": "2022-02-25T16:43:11Z",
            "properties": {"hs__test_field": "value"},
        },
    ),
    "leads": (
        "leads",
        {
            "id": "test_id",
            "createdAt": "2022-02-25T16:43:11Z",
            "updatedAt": "2022-02-25T16:43:11Z",
            "properties": {"hs__test_field": "value"},
        },
    ),
    "workflows": (
        "",
        {"id": "test_id", "insertedAt": 1675121674226, "updatedAt": 1675121674226, "enabled": True},
    ),
}


def _retriever(stream_name, config):
    stream = find_stream(stream_name, config)
    return stream, stream._stream_partition_generator._partition_factory._retriever


def _register_stream_response(requests_mock, stream_name, entity, config, records):
    """Mock everything a read of `stream_name` touches, returning `records` from its endpoint."""
    mock_dynamic_schema_requests_with_skip(requests_mock, [])

    stream, retriever = _retriever(stream_name, config)
    stream._sync_mode = SyncMode.full_refresh
    url = retriever.requester.url_base + "/" + retriever.requester.get_path(stream_slice={})
    stream._sync_mode = None

    method = retriever.requester._http_method.value
    field_path = retriever.record_selector.extractor.field_path
    data_field = field_path[0] if len(field_path) > 0 else None
    body = {data_field: records} if data_field else records
    requests_mock.register_uri(method, url, [{"json": body, "status_code": 200}])

    # CRM search streams fan out to association batch reads once they have record ids.
    if method == "POST":
        for association in retriever.requester._parameters.get("associations", []):
            requests_mock.register_uri(
                "POST",
                f"https://api.hubapi.com/crm/v4/associations/{entity}/{association}/batch/read",
                [{"json": {"results": []}, "status_code": 200}],
            )
    return stream


def _schema_for(stream_name, config, requests_mock):
    mock_dynamic_schema_requests_with_skip(requests_mock, [])
    catalog = discover(get_source(config), config).catalog.catalog
    for stream in catalog.streams:
        if stream.name == stream_name:
            return stream.json_schema
    raise AssertionError(f"{stream_name} missing from the discovered catalog")


@pytest.mark.parametrize("stream_name", list(GATED_STREAMS))
def test_read_emits_records_matching_declared_schema(stream_name, requests_mock, config):
    entity, record = GATED_STREAMS[stream_name]
    _register_stream_response(requests_mock, stream_name, entity, config, [record])

    output = read_from_stream(config, stream_name, SyncMode.full_refresh)

    # `leads` fetches properties in chunks, so one API record can surface once per chunk; assert on
    # identity rather than a count that would encode chunking internals.
    assert output.records
    assert {message.record.data["id"] for message in output.records} == {"test_id"}

    schema_properties = _schema_for(stream_name, config, requests_mock)["properties"]
    for message in output.records:
        unexpected = [field for field in message.record.data if field not in schema_properties]
        assert not unexpected, f"{stream_name} emitted fields absent from its schema: {unexpected}"


@pytest.mark.parametrize("stream_name", list(GATED_STREAMS))
def test_incremental_read_emits_state(stream_name, requests_mock, config):
    entity, record = GATED_STREAMS[stream_name]
    _register_stream_response(requests_mock, stream_name, entity, config, [record])

    output = read_from_stream(config, stream_name, SyncMode.incremental)

    assert output.records
    assert output.state_messages, f"{stream_name} produced no state message"
    assert output.most_recent_state.stream_descriptor.name == stream_name


@pytest.mark.parametrize("stream_name", list(GATED_STREAMS))
def test_empty_page_yields_no_records_and_no_error(stream_name, requests_mock, config):
    """An entitlement-limited portal legitimately returns nothing; that is not a sync failure."""
    entity, _ = GATED_STREAMS[stream_name]
    _register_stream_response(requests_mock, stream_name, entity, config, [])

    output = read_from_stream(config, stream_name, SyncMode.full_refresh)

    assert len(output.records) == 0
    assert len(output.errors) == 0


@pytest.mark.parametrize("stream_name", list(GATED_STREAMS))
def test_missing_entitlement_403_raises_actionable_error(stream_name, requests_mock, config):
    """A portal without the paid product answers 403; the sync must fail loudly, not silently."""
    entity, _ = GATED_STREAMS[stream_name]
    mock_dynamic_schema_requests_with_skip(requests_mock, [])
    stream, retriever = _retriever(stream_name, config)
    stream._sync_mode = SyncMode.full_refresh
    url = retriever.requester.url_base + "/" + retriever.requester.get_path(stream_slice={})
    stream._sync_mode = None
    requests_mock.register_uri(retriever.requester._http_method.value, url, [{"status_code": 403, "json": {}}])

    output = read_from_stream(config, stream_name, SyncMode.full_refresh)

    assert len(output.records) == 0
    assert output.errors, f"{stream_name} swallowed a 403"
    assert "Access denied (403)" in output.errors[0].trace.error.message
    assert f"to access stream {stream_name}" in output.errors[0].trace.error.message
