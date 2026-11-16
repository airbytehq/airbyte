# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import datetime as datetime_module
import json
import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from requests.models import Response

from airbyte_cdk.sources.declarative.models import (
    CustomRetriever,
    DatetimeBasedCursor,
    DeclarativeStream,
    ParentStreamConfig,
    SubstreamPartitionRouter,
)
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory


factory = ModelToComponentFactory()
resolver = ManifestReferenceResolver()
transformer = ManifestComponentTransformer()


def test_transform(components_module):
    config = {"api_key": "api_key"}
    transformator = components_module.CampaignsDetailedTransformation(config=config)
    input_record = {
        "id": "campaign_id",
        "relationships": {"campaign-messages": {"links": {"related": "https://a.klaviyo.com/api/related_link"}}},
    }

    def get_response(*args, **kwargs):
        url = kwargs["url"]
        if f"https://a.klaviyo.com/api/campaign-recipient-estimations/{input_record['id']}" == url:
            response_estimated_recipient_count = MagicMock()
            response_estimated_recipient_count.json.return_value = {"data": {"attributes": {"estimated_recipient_count": 10}}}
            return (MagicMock(), response_estimated_recipient_count)
        if url == input_record["relationships"]["campaign-messages"]["links"]["related"]:
            response_campaign_messages = MagicMock()
            response_campaign_messages.json.return_value = {"data": [{"attributes": {"field": "field"}}]}
            return (MagicMock(), response_campaign_messages)
        raise ValueError("Unexpected endpoint was called")

    transformator._http_client = MagicMock()
    transformator._http_client.send_request.side_effect = get_response

    transformator.transform(input_record)

    assert "campaign_messages" in input_record
    assert "estimated_recipient_count" in input_record


def test_transform_not_campaign_messages(components_module):
    config = {"api_key": "api_key"}
    transformator = components_module.CampaignsDetailedTransformation(config=config)
    input_record = {
        "id": "campaign_id",
        "relationships": {"campaign-messages": {"links": {"related": "https://a.klaviyo.com/api/related_link"}}},
    }

    def get_response(*args, **kwargs):
        url = kwargs["url"]
        if f"https://a.klaviyo.com/api/campaign-recipient-estimations/{input_record['id']}" == url:
            response_estimated_recipient_count = MagicMock()
            response_estimated_recipient_count.json.return_value = {"data": {"attributes": {"estimated_recipient_count": 10}}}
            return (MagicMock(), response_estimated_recipient_count)
        if url == input_record["relationships"]["campaign-messages"]["links"]["related"]:
            response_campaign_messages = MagicMock()
            response_campaign_messages.json.return_value = {}
            return (MagicMock(), response_campaign_messages)
        raise ValueError("Unexpected endpoint was called")

    transformator._http_client = MagicMock()
    transformator._http_client.send_request.side_effect = get_response

    transformator.transform(input_record)

    assert "campaign_messages" in input_record
    assert "estimated_recipient_count" in input_record


def test_transform_not_estimated_recipient_count(components_module):
    config = {"api_key": "api_key"}
    transformator = components_module.CampaignsDetailedTransformation(config=config)
    input_record = {
        "id": "campaign_id",
        "relationships": {"campaign-messages": {"links": {"related": "https://a.klaviyo.com/api/related_link"}}},
    }

    def get_response(*args, **kwargs):
        url = kwargs["url"]
        if f"https://a.klaviyo.com/api/campaign-recipient-estimations/{input_record['id']}" == url:
            response_estimated_recipient_count = MagicMock()
            response_estimated_recipient_count.json.return_value = {"data": {"attributes": {}}}
            return (MagicMock(), response_estimated_recipient_count)
        if url == input_record["relationships"]["campaign-messages"]["links"]["related"]:
            response_campaign_messages = MagicMock()
            response_campaign_messages.json.return_value = {"data": [{"attributes": {"field": "field"}}]}
            return (MagicMock(), response_campaign_messages)
        raise ValueError("Unexpected endpoint was called")

    transformator._http_client = MagicMock()
    transformator._http_client.send_request.side_effect = get_response

    transformator.transform(input_record)

    assert "campaign_messages" in input_record
    assert "estimated_recipient_count" in input_record


@pytest.mark.parametrize(
    ("state", "should_migrate"),
    (
        ({"updated_at": "2120-10-10T00:00:00+00:00", "archived": {"updated_at": "2020-10-10T00:00:00+00:00"}}, True),
        ({"updated_at": "2120-10-10T00:00:00+00:00"}, True),
        ({}, False),
        (
            {
                "states": [
                    {"partition": {"archived": "true", "campaign_type": "sms"}, "cursor": {"updated_at": "2023-10-10T00:00:00+0000"}},
                    {"partition": {"archived": "false", "campaign_type": "sms"}, "cursor": {"updated_at": "2023-10-10T00:00:00+0000"}},
                    {"partition": {"archived": "true", "campaign_type": "email"}, "cursor": {"updated_at": "2023-10-10T00:00:00+0000"}},
                    {"partition": {"archived": "false", "campaign_type": "email"}, "cursor": {"updated_at": "2023-10-10T00:00:00+0000"}},
                ]
            },
            False,
        ),
    ),
)
def test_should_migrate(components_module, state, should_migrate):
    config = {}
    declarative_stream = MagicMock()
    state_migrator = components_module.ArchivedToPerPartitionStateMigration(config=config, declarative_stream=declarative_stream)
    assert state_migrator.should_migrate(state) == should_migrate


@pytest.mark.parametrize(
    ("state", "expected_state"),
    (
        (
            {"updated_at": "2120-10-10T00:00:00+00:00", "archived": {"updated_at": "2020-10-10T00:00:00+00:00"}},
            {
                "states": [
                    {"cursor": {"updated_at": "2020-10-10T00:00:00+00:00"}, "partition": {"archived": "true"}},
                    {"cursor": {"updated_at": "2120-10-10T00:00:00+00:00"}, "partition": {"archived": "false"}},
                ]
            },
        ),
        (
            {"archived": {"updated_at": "2020-10-10T00:00:00+00:00"}},
            {
                "states": [
                    {"cursor": {"updated_at": "2020-10-10T00:00:00+00:00"}, "partition": {"archived": "true"}},
                    {"cursor": {"updated_at": "2012-01-01T00:00:00Z"}, "partition": {"archived": "false"}},
                ]
            },
        ),
        (
            {"updated_at": "2120-10-10T00:00:00+00:00"},
            {
                "states": [
                    {"cursor": {"updated_at": "2012-01-01T00:00:00Z"}, "partition": {"archived": "true"}},
                    {"cursor": {"updated_at": "2120-10-10T00:00:00+00:00"}, "partition": {"archived": "false"}},
                ]
            },
        ),
    ),
)
def test_migrate(components_module, state, expected_state):
    config = {}
    declarative_stream = MagicMock()
    declarative_stream.incremental_sync.cursor_field = "updated_at"
    state_migrator = components_module.ArchivedToPerPartitionStateMigration(config=config, declarative_stream=declarative_stream)
    assert state_migrator.migrate(state) == expected_state


@pytest.mark.parametrize(
    ("state", "expected_state"),
    (
        (
            {"updated_at": "2120-10-10T00:00:00+00:00", "archived": {"updated_at": "2020-10-10T00:00:00+00:00"}},
            {
                "states": [
                    {"cursor": {"updated_at": "2020-10-10T00:00:00+00:00"}, "partition": {"archived": "true", "campaign_type": "email"}},
                    {"cursor": {"updated_at": "2120-10-10T00:00:00+00:00"}, "partition": {"archived": "false", "campaign_type": "email"}},
                ]
            },
        ),
        (
            {"archived": {"updated_at": "2020-10-10T00:00:00+00:00"}},
            {
                "states": [
                    {"cursor": {"updated_at": "2020-10-10T00:00:00+00:00"}, "partition": {"archived": "true", "campaign_type": "email"}},
                    {"cursor": {"updated_at": "2012-01-01T00:00:00Z"}, "partition": {"archived": "false", "campaign_type": "email"}},
                ]
            },
        ),
        (
            {
                "updated_at": "2120-10-10T00:00:00+00:00",
            },
            {
                "states": [
                    {"cursor": {"updated_at": "2012-01-01T00:00:00Z"}, "partition": {"archived": "true", "campaign_type": "email"}},
                    {"cursor": {"updated_at": "2120-10-10T00:00:00+00:00"}, "partition": {"archived": "false", "campaign_type": "email"}},
                ]
            },
        ),
    ),
)
def test_migrate_campaigns(components_module, state, expected_state):
    config = {}
    declarative_stream = MagicMock()
    declarative_stream.incremental_sync.cursor_field = "updated_at"
    state_migrator = components_module.CampaignsStateMigration(config=config, declarative_stream=declarative_stream)
    assert state_migrator.migrate(state) == expected_state


@pytest.fixture
def mock_response():
    return Mock(spec=Response)


@pytest.fixture
def mock_decoder():
    return Mock()


@pytest.fixture
def mock_config():
    return Mock()


@pytest.fixture
def mock_field_path():
    return [Mock() for _ in range(2)]


@pytest.fixture
def extractor(components_module, mock_config, mock_field_path, mock_decoder):
    return components_module.KlaviyoIncludedFieldExtractor(mock_field_path, mock_config, mock_decoder)


@patch("dpath.get")
@patch("dpath.values")
def test_extract_records_by_path(mock_values, mock_get, extractor, mock_response, mock_decoder):
    mock_values.return_value = [{"key": "value"}]
    mock_get.return_value = {"key": "value"}
    mock_decoder.decode.return_value = {"data": "value"}

    field_paths = ["data"]
    records = list(extractor.extract_records_by_path(mock_response, field_paths))
    assert records == [{"key": "value"}]

    mock_values.return_value = []
    mock_get.return_value = None
    records = list(extractor.extract_records_by_path(mock_response, ["included"]))
    assert records == []


def test_update_target_records_with_included(extractor):
    target_records = [{"relationships": {"type1": {"data": {"type": "type1", "id": "1"}}}}]
    included_records = [{"id": "1", "type": "type1", "attributes": {"key": "value"}}]

    updated_records = list(extractor.update_target_records_with_included(target_records, included_records))
    assert updated_records[0]["relationships"]["type1"]["data"] == {"type": "type1", "id": "1", "key": "value"}


def test_extract_records_with_included_fields(components_module, mock_response, mock_config, mock_decoder):
    """
    Test the extraction of records with included fields from a Klaviyo API response. The API resoonse mocked is obtained
    from the API docs: https://developers.klaviyo.com/en/reference/get_events
    The JSON file is located in the mock_server folder of within the unit_tests.
    """

    # Load JSON from file
    json_path = os.path.join(os.path.dirname(__file__), "mock_server", "get_events.json")
    with open(json_path, "r") as f:
        response_json = json.load(f)

    # Update JSON to match included IDs
    response_json["data"][0]["relationships"]["profile"]["data"]["id"] = "01GDDKASAP8TKDDA2GRZDSVP4H"
    response_json["data"][0]["relationships"]["metric"]["data"]["id"] = "string"
    response_json["data"][0]["relationships"]["attributions"]["data"][0]["id"] = "925e385b52fb405715f3616c337cc65c"

    # Mock response to return the JSON
    mock_response.json.return_value = response_json
    mock_decoder.decode.return_value = response_json

    # Setup field path to extract 'data'
    mock_field_path = [Mock()]
    mock_field_path[0].eval.return_value = "data"

    # Instantiate extractor
    extractor = components_module.KlaviyoIncludedFieldExtractor(mock_field_path, mock_config, mock_decoder)

    # Extract records
    records = list(extractor.extract_records(mock_response))

    # Assert the record structure
    assert len(records) == 1
    record = records[0]

    # Print the record for debugging
    # print(json.dumps(record, indent=2))

    # Verify profile attributes
    assert record["relationships"]["profile"]["data"]["type"] == "profile"
    assert record["relationships"]["profile"]["data"]["id"] == "01GDDKASAP8TKDDA2GRZDSVP4H"
    assert record["relationships"]["profile"]["data"]["email"] == "sarah.mason@klaviyo-demo.com"
    assert record["relationships"]["profile"]["data"]["first_name"] == "Sarah"
    assert record["relationships"]["profile"]["data"]["last_name"] == "Mason"
    assert record["relationships"]["profile"]["data"]["properties"] == {"pseudonym": "Dr. Octopus"}

    # Verify metric attributes
    assert record["relationships"]["metric"]["data"]["type"] == "metric"
    assert record["relationships"]["metric"]["data"]["id"] == "string"
    assert record["relationships"]["metric"]["data"]["name"] == "string"
    assert record["relationships"]["metric"]["data"]["created"] == "string"
    assert record["relationships"]["metric"]["data"]["updated"] == "string"
    assert record["relationships"]["metric"]["data"]["integration"] == {}

    # Verify attribution attributes (empty in this case)
    assert len(record["relationships"]["attributions"]["data"]) == 1
    assert record["relationships"]["attributions"]["data"][0]["type"] == "attribution"
    assert record["relationships"]["attributions"]["data"][0]["id"] == "925e385b52fb405715f3616c337cc65c"
    # No attributes should be added since included attribution has empty attributes
    assert len(record["relationships"]["attributions"]["data"][0]) == 3  # type, id, and relationships

    # Verify attribution relationships
    assert "relationships" in record["relationships"]["attributions"]["data"][0]
    attribution_relationships = record["relationships"]["attributions"]["data"][0]["relationships"]

    # Check each nested relationship
    assert "event" in attribution_relationships
    assert attribution_relationships["event"]["data"]["type"] == "event"
    assert attribution_relationships["event"]["data"]["id"] == "string"

    assert "attributed-event" in attribution_relationships
    assert attribution_relationships["attributed-event"]["data"]["type"] == "event"
    assert attribution_relationships["attributed-event"]["data"]["id"] == "string"

    assert "campaign" in attribution_relationships
    assert attribution_relationships["campaign"]["data"]["type"] == "campaign"
    assert attribution_relationships["campaign"]["data"]["id"] == "string"

    assert "campaign-message" in attribution_relationships
    assert attribution_relationships["campaign-message"]["data"]["type"] == "campaign-message"
    assert attribution_relationships["campaign-message"]["data"]["id"] == "string"

    assert "flow" in attribution_relationships
    assert attribution_relationships["flow"]["data"]["type"] == "flow"
    assert attribution_relationships["flow"]["data"]["id"] == "string"

    assert "flow-message" in attribution_relationships
    assert attribution_relationships["flow-message"]["data"]["type"] == "flow-message"
    assert attribution_relationships["flow-message"]["data"]["id"] == "string"

    assert "flow-message-variation" in attribution_relationships
    assert attribution_relationships["flow-message-variation"]["data"]["type"] == "flow-message"
    assert attribution_relationships["flow-message-variation"]["data"]["id"] == "string"


def test_migrate_a_valid_legacy_state_to_per_partition(components_module):
    input_state = {
        "states": [
            {"partition": {"parent_id": "13506132"}, "cursor": {"last_changed": "2023-12-27T08:34:39+00:00"}},
            {"partition": {"parent_id": "14351124"}, "cursor": {"last_changed": "2022-12-27T08:35:39+00:00"}},
        ]
    }

    migrator = _migrator(components_module)

    assert migrator.should_migrate(input_state)

    expected_state = {"last_changed": "2022-12-27T08:35:39+00:00"}

    assert migrator.migrate(input_state) == expected_state


def test_should_not_migrate(components_module):
    input_state = {"last_changed": "2022-12-27T08:35:39+00:00"}
    migrator = _migrator(components_module)
    assert not migrator.should_migrate(input_state)


def test_migrate_a_valid_legacy_substream_state_to_single_state(components_module):
    input_state = {
        "states": [
            {"partition": {"event_id": "13506132"}, "cursor": {"datetime": "2023-12-27T08:34:39+00:00"}},
            {"partition": {"event_id": "14351124"}, "cursor": {"datetime": "2022-12-27T08:35:39+00:00"}},
        ]
    }

    migrator = _migrator(components_module, cursor_field="datetime")

    assert migrator.should_migrate(input_state)

    expected_state = {"datetime": "2022-12-27T08:35:39+00:00"}

    assert migrator.migrate(input_state) == expected_state


def test_should_not_migrate_concurrent_per_partition_state(components_module):
    input_state = {
        "use_global_cursor": False,
        "states": [
            {"partition": {"event_metric_id": "AAA111"}, "cursor": {"datetime": "2023-12-27T08:34:39+00:00"}},
            {"partition": {"event_metric_id": "BBB222"}, "cursor": {"datetime": "2022-12-27T08:35:39+00:00"}},
        ],
        "state": {"datetime": "2022-12-27T08:35:39+00:00"},
        "lookback_window": 0,
    }

    migrator = _migrator(components_module, cursor_field="datetime")

    assert not migrator.should_migrate(input_state)
    assert migrator.migrate(input_state) == input_state


@pytest.mark.parametrize(
    ("input_state", "should_migrate"),
    (
        ({"states": []}, False),
        ({"states": [{"cursor": {"datetime": "2023-12-27T08:34:39+00:00"}}]}, True),
        ({"states": [{"partition": None, "cursor": {"datetime": "2023-12-27T08:34:39+00:00"}}]}, True),
    ),
)
def test_should_migrate_states_without_partitions(components_module, input_state, should_migrate):
    migrator = _migrator(components_module, cursor_field="datetime")
    assert migrator.should_migrate(input_state) == should_migrate


def _migrator(components_module, cursor_field="last_changed"):
    partition_router = SubstreamPartitionRouter(
        type="SubstreamPartitionRouter",
        parent_stream_configs=[
            ParentStreamConfig(
                type="ParentStreamConfig",
                parent_key="{{ parameters['parent_key_id'] }}",
                partition_field="parent_id",
                stream=DeclarativeStream(
                    type="DeclarativeStream", retriever=CustomRetriever(type="CustomRetriever", class_name="a_class_name")
                ),
            )
        ],
    )
    cursor = DatetimeBasedCursor(
        type="DatetimeBasedCursor",
        cursor_field="{{ parameters['cursor_field'] }}",
        datetime_format="%Y-%m-%dT%H:%M:%S.%fZ",
        start_datetime="1970-01-01T00:00:00.0Z",
    )
    config = {}
    parameters = {"cursor_field": cursor_field, "parent_key_id": "id"}

    declarative_stream = MagicMock()
    declarative_stream.retriever.partition_router = partition_router
    declarative_stream.incremental_sync = cursor
    declarative_stream.parameters = parameters

    return components_module.PerPartitionToSingleStateMigration(config=config, declarative_stream=declarative_stream)


def _flow_series_response(body):
    response = Mock(spec=Response)
    response.json.return_value = body
    return response


def _per_day_extractor(components_module):
    return components_module.FlowSeriesPerDayExtractor()


def test_flow_series_per_day_extractor_splits_response_into_one_record_per_day(components_module):
    """
    Two groupings over three days must produce six records, each carrying the calendar day it
    reports on and the statistics value sitting at that day's index.
    """
    body = {
        "data": {
            "type": "flow-series-report",
            "attributes": {
                "date_times": [
                    "2024-01-05T00:00:00+00:00",
                    "2024-01-06T00:00:00+00:00",
                    "2024-01-07T00:00:00+00:00",
                ],
                "results": [
                    {
                        "groupings": {"flow_id": "XVTP5Q", "send_channel": "email", "flow_message_id": "msg_a"},
                        "statistics": {"opens": [123, 156, 144], "open_rate": [0.8253, 0.8722, 0.8398]},
                    },
                    {
                        "groupings": {"flow_id": "XVTP5Q", "send_channel": "email", "flow_message_id": "msg_b"},
                        "statistics": {"opens": [97, 98, 65], "open_rate": [0.7562, 0.761, 0.688]},
                    },
                ],
            },
        }
    }

    records = list(_per_day_extractor(components_module).extract_records(_flow_series_response(body)))

    assert len(records) == 6
    assert [record["date"] for record in records] == [
        "2024-01-05T00:00:00+00:00",
        "2024-01-06T00:00:00+00:00",
        "2024-01-07T00:00:00+00:00",
    ] * 2
    assert [record["statistics"]["opens"] for record in records] == [123, 156, 144, 97, 98, 65]
    assert [record["statistics"]["open_rate"] for record in records] == [0.8253, 0.8722, 0.8398, 0.7562, 0.761, 0.688]
    assert records[0]["groupings"] == {"flow_id": "XVTP5Q", "send_channel": "email", "flow_message_id": "msg_a"}
    assert records[3]["groupings"]["flow_message_id"] == "msg_b"


@pytest.mark.parametrize(
    "attributes",
    [
        pytest.param({"results": [{"groupings": {}, "statistics": {"opens": [1, 2]}}]}, id="no_date_times"),
        pytest.param({"date_times": [], "results": [{"groupings": {}, "statistics": {"opens": []}}]}, id="empty_date_times"),
        pytest.param({"date_times": ["2024-01-05T00:00:00+00:00"]}, id="no_results"),
        pytest.param({}, id="empty_attributes"),
    ],
)
def test_flow_series_per_day_extractor_yields_nothing_without_days_or_results(components_module, attributes):
    """A response missing either side of the alignment produces no records instead of raising."""
    body = {"data": {"attributes": attributes}}

    assert list(_per_day_extractor(components_module).extract_records(_flow_series_response(body))) == []


def test_flow_series_per_day_extractor_fills_missing_statistics_with_none(components_module):
    """
    A statistics array shorter than date_times must report null for the days it does not cover.
    Reusing the last known value or shifting values onto earlier days would silently misdate data.
    """
    body = {
        "data": {
            "attributes": {
                "date_times": [
                    "2024-01-05T00:00:00+00:00",
                    "2024-01-06T00:00:00+00:00",
                    "2024-01-07T00:00:00+00:00",
                ],
                "results": [
                    {
                        "groupings": {"flow_id": "XVTP5Q"},
                        "statistics": {"opens": [123], "clicks": None, "conversions": [1, 2, 3]},
                    }
                ],
            }
        }
    }

    records = list(_per_day_extractor(components_module).extract_records(_flow_series_response(body)))

    assert [record["statistics"]["opens"] for record in records] == [123, None, None]
    assert [record["statistics"]["clicks"] for record in records] == [None, None, None]
    assert [record["statistics"]["conversions"] for record in records] == [1, 2, 3]


def test_flow_series_reports_schema_matches_requested_statistics():
    """
    Guard against the request body and the declared schema drifting apart: every statistic the
    connector asks Klaviyo for needs a scalar property in the schema, and nothing else.
    """
    import yaml

    manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manifest.yaml")
    with open(manifest_path) as manifest_file:
        manifest = yaml.safe_load(manifest_file)

    stream = manifest["definitions"]["streams"]["flow_series_reports"]
    requested = stream["retriever"]["requester"]["request_body_json"]["data"]["attributes"]["statistics"]
    declared = manifest["schemas"]["flow_series_reports"]["properties"]["statistics"]["properties"]

    assert sorted(requested) == sorted(declared)
    for name, definition in declared.items():
        assert definition["type"] == ["null", "number"], f"{name} must be a scalar number, one value per day"
        assert "items" not in definition, f"{name} still declares array items"


def _manifest():
    import yaml

    manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manifest.yaml")
    with open(manifest_path) as manifest_file:
        return yaml.safe_load(manifest_file)


def _report_windows(stream_name, config, now, stream_state=None):
    """
    Build the stream's real cursor straight from the manifest and return the report windows it
    would request, as (start, end) datetimes. Pass `stream_state` to measure a resumed sync.
    """
    import freezegun

    from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager

    definition = _manifest()["definitions"]["streams"][stream_name]["incremental_sync"]
    local_factory = ModelToComponentFactory()
    local_factory._connector_state_manager = ConnectorStateManager()
    with freezegun.freeze_time(now):
        cursor = local_factory.create_concurrent_cursor_from_datetime_based_cursor(
            model_type=DatetimeBasedCursor,
            component_definition=definition,
            stream_name=stream_name,
            stream_namespace=None,
            stream_state=stream_state or {},
            config=config,
        )
        return [
            (
                datetime_module.datetime.strptime(slice_.cursor_slice["start_time"], "%Y-%m-%dT%H:%M:%S%z"),
                datetime_module.datetime.strptime(slice_.cursor_slice["end_time"], "%Y-%m-%dT%H:%M:%S%z"),
            )
            for slice_ in cursor.stream_slices()
        ]


_REPORT_WINDOWS_NOW = "2024-06-15T12:34:56+00:00"
_LAST_COMPLETE_DAY = datetime_module.date(2024, 6, 14)
_MIDNIGHT = datetime_module.time(0, 0, 0)
_END_OF_DAY = datetime_module.time(23, 59, 59)
_STORED_CURSOR = {"date": "2024-05-02T00:00:00+00:00"}


@pytest.mark.parametrize("stream_name", ["flow_series_reports", "campaign_values_reports"])
@pytest.mark.parametrize(
    "case, start_date, stream_state, lookback",
    [
        ("first sync from midnight", "2024-01-01T00:00:00Z", None, 0),
        ("first sync from a start date with a time of day", "2024-01-01T05:30:00Z", None, 0),
        ("first sync from a start date one second before midnight", "2024-01-01T23:59:59Z", None, 0),
        ("resumed from a stored cursor", "2024-01-01T00:00:00Z", _STORED_CURSOR, 0),
        ("resumed from a stored cursor with a 5 day lookback", "2024-01-01T00:00:00Z", _STORED_CURSOR, 5),
    ],
)
def test_report_windows_are_whole_calendar_days(stream_name, case, start_date, stream_state, lookback):
    """
    Klaviyo report timeframes are inclusive on both ends and round the end up to :59:59 of its
    hour, so a window that stops mid-day reports that day and so does the next window, which
    double-counts it. Every window must therefore begin at midnight and the last one must stop at
    the end of the last complete day - not at the moment the sync happens to run, which would both
    report a partial day and leave a mid-day cursor for the next sync to resume from. Consecutive
    windows must neither share nor skip a calendar day, whatever time of day the configured start
    date carries and whether the sync starts fresh or resumes from a stored cursor.
    """
    config = {"start_date": start_date, "reporting_lookback_window": lookback}
    windows = _report_windows(stream_name, config, _REPORT_WINDOWS_NOW, stream_state=stream_state)

    assert len(windows) > 1, f"{case}: expected several 30-day windows, got {windows}"
    for start, _ in windows:
        assert start.time() == _MIDNIGHT, f"{case}: window starts mid-day: {start.isoformat()}"
    last_end = windows[-1][1]
    assert (
        last_end.time() == _END_OF_DAY
    ), f"{case}: the last window ends mid-day at {last_end.isoformat()}, so it reports a partial day the next sync reports again"
    assert (
        last_end.date() == _LAST_COMPLETE_DAY
    ), f"{case}: the last window ends on {last_end.date()} instead of the last complete day {_LAST_COMPLETE_DAY}"
    for (_, earlier_end), (later_start, _) in zip(windows, windows[1:]):
        assert (
            earlier_end.date() < later_start.date()
        ), f"{case}: windows share the day {earlier_end.date()}: {earlier_end.isoformat()} then {later_start.isoformat()}"
        assert (later_start.date() - earlier_end.date()).days == 1, (
            f"{case}: the day after {earlier_end.date()} is in no window at all, so a day of data is lost "
            f"before {later_start.isoformat()}"
        )


def test_only_flow_series_reports_offers_a_reporting_lookback_window():
    """
    campaign_values_reports takes no `interval`, so one request yields a single aggregate over the
    whole window, keyed by the day boundary that closes it. Re-reading a period there cannot
    replace anything, it can only add a second differently-keyed row covering the same days.
    """
    streams = _manifest()["definitions"]["streams"]

    assert "lookback_window" in streams["flow_series_reports"]["incremental_sync"]
    assert "lookback_window" not in streams["campaign_values_reports"]["incremental_sync"]
    assert "interval" in streams["flow_series_reports"]["retriever"]["requester"]["request_body_json"]["data"]["attributes"]
    assert "interval" not in streams["campaign_values_reports"]["retriever"]["requester"]["request_body_json"]["data"]["attributes"]
