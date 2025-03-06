# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

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
    target_records = [{"relationships": {"type1": {"data": {"id": 1}}}}]
    included_records = [{"id": 1, "type": "type1", "attributes": {"key": "value"}}]

    updated_records = list(extractor.update_target_records_with_included(target_records, included_records))
    assert updated_records[0]["relationships"]["type1"]["data"] == {"id": 1, "key": "value"}


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


def _migrator(components_module):
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
    parameters = {"cursor_field": "last_changed", "parent_key_id": "id"}

    declarative_stream = MagicMock()
    declarative_stream.retriever.partition_router = partition_router
    declarative_stream.incremental_sync = cursor
    declarative_stream.parameters = parameters

    return components_module.PerPartitionToSingleStateMigration(config=config, declarative_stream=declarative_stream)
