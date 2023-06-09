#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.connector_builder.message_grouper import MessageGrouper
from airbyte_cdk.connector_builder.models import HttpRequest, HttpResponse, LogMessage, StreamRead, StreamReadPages
from airbyte_cdk.models import (
    AirbyteControlConnectorConfigMessage,
    AirbyteControlMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    Level,
    OrchestratorType,
)
from airbyte_cdk.models import Type as MessageType
from unit_tests.connector_builder.utils import create_configured_catalog

MAX_PAGES_PER_SLICE = 4
MAX_SLICES = 3

MANIFEST = {
    "version": "0.30.0",
    "type": "DeclarativeSource",
    "definitions": {
        "selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
        "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "DeclarativeSource"},
        "retriever": {
            "type": "DeclarativeSource",
            "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
            "paginator": {"type": "NoPagination"},
            "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
        },
        "hashiras_stream": {
            "retriever": {
                "type": "DeclarativeSource",
                "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$parameters": {"name": "hashiras", "path": "/hashiras"},
        },
        "breathing_techniques_stream": {
            "retriever": {
                "type": "DeclarativeSource",
                "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$parameters": {"name": "breathing-techniques", "path": "/breathing_techniques"},
        },
    },
    "streams": [
        {
            "type": "DeclarativeStream",
            "retriever": {
                "type": "SimpleRetriever",
                "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$parameters": {"name": "hashiras", "path": "/hashiras"},
        },
        {
            "type": "DeclarativeStream",
            "retriever": {
                "type": "SimpleRetriever",
                "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$parameters": {"name": "breathing-techniques", "path": "/breathing_techniques"},
        },
    ],
    "check": {"stream_names": ["hashiras"], "type": "CheckStream"},
}

CONFIG = {"rank": "upper-six"}

A_SOURCE = MagicMock()


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_get_grouped_messages(mock_entrypoint_read):
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "http_method": "GET",
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}', "http_method": "GET"}
    expected_schema = {"$schema": "http://json-schema.org/schema#", "properties": {"name": {"type": "string"}, "date": {"type": "string"}}, "type": "object"}
    expected_datetime_fields = {"date":"%Y-%m-%d"}
    expected_pages = [
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
            records=[{"name": "Shinobu Kocho", "date": "2023-03-03"}, {"name": "Muichiro Tokito", "date": "2023-03-04"}],
        ),
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
            records=[{"name": "Mitsuri Kanroji", "date": "2023-03-05"}],
        ),
    ]

    mock_source = make_mock_source(mock_entrypoint_read, iter(
        [
            request_log_message(request),
            response_log_message(response),
            record_message("hashiras", {"name": "Shinobu Kocho", "date": "2023-03-03"}),
            record_message("hashiras", {"name": "Muichiro Tokito", "date": "2023-03-04"}),
            request_log_message(request),
            response_log_message(response),
            record_message("hashiras", {"name": "Mitsuri Kanroji", "date": "2023-03-05"}),
        ]
    ))

    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    actual_response: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert actual_response.inferred_schema == expected_schema
    assert actual_response.inferred_datetime_formats == expected_datetime_fields

    single_slice = actual_response.slices[0]
    for i, actual_page in enumerate(single_slice.pages):
        assert actual_page == expected_pages[i]


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_get_grouped_messages_with_logs(mock_entrypoint_read):
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
        "http_method": "GET",
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    expected_pages = [
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
            records=[{"name": "Shinobu Kocho"}, {"name": "Muichiro Tokito"}],
        ),
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
            records=[{"name": "Mitsuri Kanroji"}],
        ),
    ]
    expected_logs = [
        LogMessage(**{"message": "log message before the request", "level": "INFO"}),
        LogMessage(**{"message": "log message during the page", "level": "INFO"}),
        LogMessage(**{"message": "log message after the response", "level": "INFO"}),
    ]

    mock_source = make_mock_source(mock_entrypoint_read, iter(
            [
                AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message before the request")),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message during the page")),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message after the response")),
            ]
        )
    )

    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    actual_response: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )
    single_slice = actual_response.slices[0]
    for i, actual_page in enumerate(single_slice.pages):
        assert actual_page == expected_pages[i]

    for i, actual_log in enumerate(actual_response.logs):
        assert actual_log == expected_logs[i]


@pytest.mark.parametrize(
    "request_record_limit, max_record_limit",
    [
        pytest.param(1, 3, id="test_create_request_with_record_limit"),
        pytest.param(3, 1, id="test_create_request_record_limit_exceeds_max"),
    ],
)
@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_get_grouped_messages_record_limit(mock_entrypoint_read, request_record_limit, max_record_limit):
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    mock_source = make_mock_source(mock_entrypoint_read, iter(
            [
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
                response_log_message(response),
            ]
        )
    )
    n_records = 2
    record_limit = min(request_record_limit, max_record_limit)

    api = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES, max_record_limit=max_record_limit)
    actual_response: StreamRead = api.get_message_groups(
        mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras"), record_limit=request_record_limit
    )
    single_slice = actual_response.slices[0]
    total_records = 0
    for i, actual_page in enumerate(single_slice.pages):
        total_records += len(actual_page.records)
    assert total_records == min([record_limit, n_records])


@pytest.mark.parametrize(
    "max_record_limit",
    [
        pytest.param(2, id="test_create_request_no_record_limit"),
        pytest.param(1, id="test_create_request_no_record_limit_n_records_exceed_max"),
    ],
)
@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_get_grouped_messages_default_record_limit(mock_entrypoint_read, max_record_limit):
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    mock_source = make_mock_source(mock_entrypoint_read, iter(
            [
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
                response_log_message(response),
            ]
        )
    )
    n_records = 2

    api = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES, max_record_limit=max_record_limit)
    actual_response: StreamRead = api.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )
    single_slice = actual_response.slices[0]
    total_records = 0
    for i, actual_page in enumerate(single_slice.pages):
        total_records += len(actual_page.records)
    assert total_records == min([max_record_limit, n_records])


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_get_grouped_messages_limit_0(mock_entrypoint_read):
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    mock_source = make_mock_source(mock_entrypoint_read, iter(
            [
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
                response_log_message(response),
            ]
        )
    )
    api = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    with pytest.raises(ValueError):
        api.get_message_groups(source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras"), record_limit=0)


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_get_grouped_messages_no_records(mock_entrypoint_read):
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
        "http_method": "GET",
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    expected_pages = [
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
            records=[],
        ),
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
            records=[],
        ),
    ]

    mock_source = make_mock_source(mock_entrypoint_read, iter(
            [
                request_log_message(request),
                response_log_message(response),
                request_log_message(request),
                response_log_message(response),
            ]
        )
    )

    message_grouper = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    actual_response: StreamRead = message_grouper.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    single_slice = actual_response.slices[0]
    for i, actual_page in enumerate(single_slice.pages):
        assert actual_page == expected_pages[i]


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_get_grouped_messages_invalid_group_format(mock_entrypoint_read):
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}

    mock_source = make_mock_source(mock_entrypoint_read, iter(
            [
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
            ]
        )
    )

    api = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    with pytest.raises(ValueError):
        api.get_message_groups(source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras"))


@pytest.mark.parametrize(
    "log_message, expected_response",
    [
        pytest.param(
            {"status_code": 200, "headers": {"field": "name"}, "body": '{"id": "fire", "owner": "kyojuro_rengoku"}'},
            HttpResponse(status=200, headers={"field": "name"}, body='{"id": "fire", "owner": "kyojuro_rengoku"}'),
            id="test_create_response_with_all_fields",
        ),
        pytest.param(
            {"status_code": 200, "headers": {"field": "name"}},
            HttpResponse(status=200, headers={"field": "name"}, body="{}"),
            id="test_create_response_with_no_body",
        ),
        pytest.param(
            {"status_code": 200, "body": '{"id": "fire", "owner": "kyojuro_rengoku"}'},
            HttpResponse(status=200, body='{"id": "fire", "owner": "kyojuro_rengoku"}'),
            id="test_create_response_with_no_headers",
        ),
        pytest.param(
            {
                "status_code": 200,
                "headers": {"field": "name"},
                "body": '[{"id": "fire", "owner": "kyojuro_rengoku"}, {"id": "mist", "owner": "muichiro_tokito"}]',
            },
            HttpResponse(
                status=200,
                headers={"field": "name"},
                body='[{"id": "fire", "owner": "kyojuro_rengoku"}, {"id": "mist", "owner": "muichiro_tokito"}]',
            ),
            id="test_create_response_with_array",
        ),
        pytest.param(
            {"status_code": 200, "body": "tomioka"},
            HttpResponse(status=200, body="tomioka"),
            id="test_create_response_with_string",
        ),
        pytest.param("request:{invalid_json: }", None, id="test_invalid_json_still_does_not_crash"),
        pytest.param("just a regular log message", None, id="test_no_response:_prefix_does_not_crash"),
    ],
)
def test_create_response_from_log_message(log_message, expected_response):
    if isinstance(log_message, str):
        response_message = log_message
    else:
        response_message = f"response:{json.dumps(log_message)}"

    airbyte_log_message = AirbyteLogMessage(level=Level.INFO, message=response_message)
    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    actual_response = connector_builder_handler._create_response_from_log_message(airbyte_log_message)

    assert actual_response == expected_response


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_get_grouped_messages_with_many_slices(mock_entrypoint_read):
    request = {}
    response = {"status_code": 200}

    mock_source = make_mock_source(mock_entrypoint_read, iter(
            [
                slice_message('{"descriptor": "first_slice"}'),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                slice_message('{"descriptor": "second_slice"}'),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Obanai Iguro"}),
                request_log_message(request),
                response_log_message(response),
            ]
        )
    )

    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    stream_read: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert not stream_read.test_read_limit_reached
    assert len(stream_read.slices) == 2

    assert stream_read.slices[0].slice_descriptor == {"descriptor": "first_slice"}
    assert len(stream_read.slices[0].pages) == 1
    assert len(stream_read.slices[0].pages[0].records) == 1

    assert stream_read.slices[1].slice_descriptor == {"descriptor": "second_slice"}
    assert len(stream_read.slices[1].pages) == 3
    assert len(stream_read.slices[1].pages[0].records) == 2
    assert len(stream_read.slices[1].pages[1].records) == 1
    assert len(stream_read.slices[1].pages[2].records) == 0


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_get_grouped_messages_given_maximum_number_of_slices_then_test_read_limit_reached(mock_entrypoint_read):
    maximum_number_of_slices = 5
    request = {}
    response = {"status_code": 200}
    mock_source = make_mock_source(mock_entrypoint_read, iter([slice_message(), request_log_message(request), response_log_message(response)] * maximum_number_of_slices))

    api = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    stream_read: StreamRead = api.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.test_read_limit_reached


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_get_grouped_messages_given_maximum_number_of_pages_then_test_read_limit_reached(mock_entrypoint_read):
    maximum_number_of_pages_per_slice = 5
    request = {}
    response = {"status_code": 200}
    mock_source = make_mock_source(mock_entrypoint_read, iter([slice_message()] + [request_log_message(request), response_log_message(response)] * maximum_number_of_pages_per_slice))

    api = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    stream_read: StreamRead = api.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.test_read_limit_reached


def test_read_stream_returns_error_if_stream_does_not_exist():
    mock_source = MagicMock()
    mock_source.read.side_effect = ValueError("error")

    full_config = {**CONFIG, **{"__injected_declarative_manifest": MANIFEST}}

    message_grouper = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    actual_response = message_grouper.get_message_groups(source=mock_source, config=full_config,
                                                         configured_catalog=create_configured_catalog("not_in_manifest"))

    assert 1 == len(actual_response.logs)
    assert "Traceback" in actual_response.logs[0].message
    assert "ERROR" in actual_response.logs[0].level


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_given_control_message_then_stream_read_has_config_update(mock_entrypoint_read):
    updated_config = {"x": 1}
    mock_source = make_mock_source(mock_entrypoint_read, iter(
        any_request_and_response_with_a_record() + [connector_configuration_control_message(1, updated_config)]
    ))
    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    stream_read: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.latest_config_update == updated_config


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_given_no_control_message_then_use_in_memory_config_change_as_update(mock_entrypoint_read):
    mock_source = make_mock_source(mock_entrypoint_read, iter(any_request_and_response_with_a_record()))
    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    full_config = {**CONFIG, **{"__injected_declarative_manifest": MANIFEST}}
    stream_read: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=full_config, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.latest_config_update == CONFIG


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_given_multiple_control_messages_then_stream_read_has_latest_based_on_emitted_at(mock_entrypoint_read):
    earliest = 0
    earliest_config = {"earliest": 0}
    latest = 1
    latest_config = {"latest": 1}
    mock_source = make_mock_source(mock_entrypoint_read, iter(
        any_request_and_response_with_a_record() +
        [
            # here, we test that even if messages are emitted in a different order, we still rely on `emitted_at`
            connector_configuration_control_message(latest, latest_config),
            connector_configuration_control_message(earliest, earliest_config),
        ]
    )
                                   )
    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    stream_read: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.latest_config_update == latest_config


@patch('airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read')
def test_given_multiple_control_messages_with_same_timestamp_then_stream_read_has_latest_based_on_message_order(mock_entrypoint_read):
    emitted_at = 0
    earliest_config = {"earliest": 0}
    latest_config = {"latest": 1}
    mock_source = make_mock_source(mock_entrypoint_read, iter(
        any_request_and_response_with_a_record() +
        [
            connector_configuration_control_message(emitted_at, earliest_config),
            connector_configuration_control_message(emitted_at, latest_config),
        ]
    )
                                   )
    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    stream_read: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.latest_config_update == latest_config


def make_mock_source(mock_entrypoint_read, return_value: Iterator) -> MagicMock:
    mock_source = MagicMock()
    mock_entrypoint_read.return_value = return_value
    return mock_source


def request_log_message(request: dict) -> AirbyteMessage:
    return AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"request:{json.dumps(request)}"))


def response_log_message(response: dict) -> AirbyteMessage:
    return AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"response:{json.dumps(response)}"))


def record_message(stream: str, data: dict) -> AirbyteMessage:
    return AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=1234))


def slice_message(slice_descriptor: str = '{"key": "value"}') -> AirbyteMessage:
    return AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message="slice:" + slice_descriptor))


def connector_configuration_control_message(emitted_at: float, config: dict) -> AirbyteMessage:
    return AirbyteMessage(
        type=MessageType.CONTROL,
        control=AirbyteControlMessage(
            type=OrchestratorType.CONNECTOR_CONFIG,
            emitted_at=emitted_at,
            connectorConfig=AirbyteControlConnectorConfigMessage(config=config),
        )
    )


def any_request_and_response_with_a_record():
    return [
        request_log_message({"request": 1}),
        response_log_message({"response": 2}),
        record_message("hashiras", {"name": "Shinobu Kocho"}),
    ]
