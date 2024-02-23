#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Iterator, List, Mapping
from unittest.mock import MagicMock, Mock, patch

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


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_get_grouped_messages(mock_entrypoint_read: Mock) -> None:
    url = "https://demonslayers.com/api/v1/hashiras?era=taisho"
    request = {
        "headers": {"Content-Type": "application/json"},
        "method": "GET",
        "body": {"content": '{"custom": "field"}'},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": {"content": '{"name": "field"}'}}
    expected_schema = {
        "$schema": "http://json-schema.org/schema#",
        "properties": {"name": {"type": "string"}, "date": {"type": "string"}},
        "type": "object",
    }
    expected_datetime_fields = {"date": "%Y-%m-%d"}
    expected_pages = [
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body='{"custom": "field"}',
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
                body='{"custom": "field"}',
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
            records=[{"name": "Mitsuri Kanroji", "date": "2023-03-05"}],
        ),
    ]

    mock_source = make_mock_source(
        mock_entrypoint_read,
        iter(
            [
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Shinobu Kocho", "date": "2023-03-03"}),
                record_message("hashiras", {"name": "Muichiro Tokito", "date": "2023-03-04"}),
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Mitsuri Kanroji", "date": "2023-03-05"}),
            ]
        ),
    )

    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    actual_response: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert actual_response.inferred_schema == expected_schema
    assert actual_response.inferred_datetime_formats == expected_datetime_fields

    single_slice = actual_response.slices[0]
    for i, actual_page in enumerate(single_slice.pages):
        assert actual_page == expected_pages[i]


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_get_grouped_messages_with_logs(mock_entrypoint_read: Mock) -> None:
    url = "https://demonslayers.com/api/v1/hashiras?era=taisho"
    request = {
        "headers": {"Content-Type": "application/json"},
        "method": "GET",
        "body": {"content": '{"custom": "field"}'},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": {"content": '{"name": "field"}'}}
    expected_pages = [
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body='{"custom": "field"}',
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
                body='{"custom": "field"}',
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

    mock_source = make_mock_source(
        mock_entrypoint_read,
        iter(
            [
                AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message before the request")),
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message during the page")),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message after the response")),
            ]
        ),
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
    "request_record_limit, max_record_limit, should_fail",
    [
        pytest.param(1, 3, False, id="test_create_request_with_record_limit"),
        pytest.param(3, 1, True, id="test_create_request_record_limit_exceeds_max"),
    ],
)
@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_get_grouped_messages_record_limit(mock_entrypoint_read: Mock, request_record_limit: int, max_record_limit: int, should_fail: bool) -> None:
    url = "https://demonslayers.com/api/v1/hashiras?era=taisho"
    request = {
        "headers": {"Content-Type": "application/json"},
        "method": "GET",
        "body": {"content": '{"custom": "field"}'},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": {"content": '{"name": "field"}'}}
    mock_source = make_mock_source(
        mock_entrypoint_read,
        iter(
            [
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
            ]
        ),
    )
    n_records = 2
    record_limit = min(request_record_limit, max_record_limit)

    api = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES, max_record_limit=max_record_limit)
    # this is the call we expect to raise an exception
    if should_fail:
        with pytest.raises(ValueError):
            api.get_message_groups(
                mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras"), record_limit=request_record_limit
            )
    else:
        actual_response: StreamRead = api.get_message_groups(
            mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras"), record_limit=request_record_limit
        )
        single_slice = actual_response.slices[0]
        total_records = 0
        for i, actual_page in enumerate(single_slice.pages):
            total_records += len(actual_page.records)
        assert total_records == min([record_limit, n_records])

        assert (total_records >= max_record_limit) == actual_response.test_read_limit_reached


@pytest.mark.parametrize(
    "max_record_limit",
    [
        pytest.param(2, id="test_create_request_no_record_limit"),
        pytest.param(1, id="test_create_request_no_record_limit_n_records_exceed_max"),
    ],
)
@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_get_grouped_messages_default_record_limit(mock_entrypoint_read: Mock, max_record_limit: int) -> None:
    url = "https://demonslayers.com/api/v1/hashiras?era=taisho"
    request = {
        "headers": {"Content-Type": "application/json"},
        "method": "GET",
        "body": {"content": '{"custom": "field"}'},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": {"content": '{"name": "field"}'}}
    mock_source = make_mock_source(
        mock_entrypoint_read,
        iter(
            [
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
            ]
        ),
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


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_get_grouped_messages_limit_0(mock_entrypoint_read: Mock) -> None:
    url = "https://demonslayers.com/api/v1/hashiras?era=taisho"
    request = {
        "headers": {"Content-Type": "application/json"},
        "method": "GET",
        "body": {"content": '{"custom": "field"}'},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": {"content": '{"name": "field"}'}}
    mock_source = make_mock_source(
        mock_entrypoint_read,
        iter(
            [
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
            ]
        ),
    )
    api = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    with pytest.raises(ValueError):
        api.get_message_groups(source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras"), record_limit=0)


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_get_grouped_messages_no_records(mock_entrypoint_read: Mock) -> None:
    url = "https://demonslayers.com/api/v1/hashiras?era=taisho"
    request = {
        "headers": {"Content-Type": "application/json"},
        "method": "GET",
        "body": {"content": '{"custom": "field"}'},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": {"content": '{"name": "field"}'}}
    expected_pages = [
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body='{"custom": "field"}',
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
                body='{"custom": "field"}',
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
            records=[],
        ),
    ]

    mock_source = make_mock_source(
        mock_entrypoint_read,
        iter(
            [
                request_response_log_message(request, response, url),
                request_response_log_message(request, response, url),
            ]
        ),
    )

    message_grouper = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    actual_response: StreamRead = message_grouper.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    single_slice = actual_response.slices[0]
    for i, actual_page in enumerate(single_slice.pages):
        assert actual_page == expected_pages[i]


@pytest.mark.parametrize(
    "log_message, expected_response",
    [
        pytest.param(
            {
                "http": {
                    "response": {
                        "status_code": 200,
                        "headers": {"field": "name"},
                        "body": {"content": '{"id": "fire", "owner": "kyojuro_rengoku"}'},
                    }
                }
            },
            HttpResponse(status=200, headers={"field": "name"}, body='{"id": "fire", "owner": "kyojuro_rengoku"}'),
            id="test_create_response_with_all_fields",
        ),
        pytest.param(
            {"http": {"response": {"status_code": 200, "headers": {"field": "name"}}}},
            HttpResponse(status=200, headers={"field": "name"}, body=""),
            id="test_create_response_with_no_body",
        ),
        pytest.param(
            {"http": {"response": {"status_code": 200, "body": {"content": '{"id": "fire", "owner": "kyojuro_rengoku"}'}}}},
            HttpResponse(status=200, body='{"id": "fire", "owner": "kyojuro_rengoku"}'),
            id="test_create_response_with_no_headers",
        ),
        pytest.param(
            {
                "http": {
                    "response": {
                        "status_code": 200,
                        "headers": {"field": "name"},
                        "body": {"content": '[{"id": "fire", "owner": "kyojuro_rengoku"}, {"id": "mist", "owner": "muichiro_tokito"}]'},
                    }
                }
            },
            HttpResponse(
                status=200,
                headers={"field": "name"},
                body='[{"id": "fire", "owner": "kyojuro_rengoku"}, {"id": "mist", "owner": "muichiro_tokito"}]',
            ),
            id="test_create_response_with_array",
        ),
        pytest.param(
            {"http": {"response": {"status_code": 200, "body": {"content": "tomioka"}}}},
            HttpResponse(status=200, body="tomioka"),
            id="test_create_response_with_string",
        ),
    ],
)
def test_create_response_from_log_message(log_message: str, expected_response: HttpResponse) -> None:
    if isinstance(log_message, str):
        response_message = json.loads(log_message)
    else:
        response_message = log_message

    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    actual_response = connector_builder_handler._create_response_from_log_message(response_message)

    assert actual_response == expected_response


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_get_grouped_messages_with_many_slices(mock_entrypoint_read: Mock) -> None:
    url = "http://a-url.com"
    request: Mapping[str, Any] = {}
    response = {"status_code": 200}

    mock_source = make_mock_source(
        mock_entrypoint_read,
        iter(
            [
                slice_message('{"descriptor": "first_slice"}'),
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                slice_message('{"descriptor": "second_slice"}'),
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
                request_response_log_message(request, response, url),
                record_message("hashiras", {"name": "Obanai Iguro"}),
                request_response_log_message(request, response, url),
            ]
        ),
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


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_get_grouped_messages_given_maximum_number_of_slices_then_test_read_limit_reached(mock_entrypoint_read: Mock) -> None:
    maximum_number_of_slices = 5
    request: Mapping[str, Any] = {}
    response = {"status_code": 200}
    mock_source = make_mock_source(
        mock_entrypoint_read, iter([slice_message(), request_response_log_message(request, response, "a_url")] * maximum_number_of_slices)
    )

    api = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    stream_read: StreamRead = api.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.test_read_limit_reached


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_get_grouped_messages_given_maximum_number_of_pages_then_test_read_limit_reached(mock_entrypoint_read: Mock) -> None:
    maximum_number_of_pages_per_slice = 5
    request: Mapping[str, Any] = {}
    response = {"status_code": 200}
    mock_source = make_mock_source(
        mock_entrypoint_read,
        iter([slice_message()] + [request_response_log_message(request, response, "a_url")] * maximum_number_of_pages_per_slice),
    )

    api = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)

    stream_read: StreamRead = api.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.test_read_limit_reached


def test_read_stream_returns_error_if_stream_does_not_exist() -> None:
    mock_source = MagicMock()
    mock_source.read.side_effect = ValueError("error")

    full_config: Mapping[str, Any] = {**CONFIG, **{"__injected_declarative_manifest": MANIFEST}}

    message_grouper = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    actual_response = message_grouper.get_message_groups(
        source=mock_source, config=full_config, configured_catalog=create_configured_catalog("not_in_manifest")
    )

    assert 1 == len(actual_response.logs)
    assert "Traceback" in actual_response.logs[0].message
    assert "ERROR" in actual_response.logs[0].level


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_given_control_message_then_stream_read_has_config_update(mock_entrypoint_read: Mock) -> None:
    updated_config = {"x": 1}
    mock_source = make_mock_source(
        mock_entrypoint_read, iter(any_request_and_response_with_a_record() + [connector_configuration_control_message(1, updated_config)])
    )
    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    stream_read: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.latest_config_update == updated_config


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_given_multiple_control_messages_then_stream_read_has_latest_based_on_emitted_at(mock_entrypoint_read: Mock) -> None:
    earliest = 0
    earliest_config = {"earliest": 0}
    latest = 1
    latest_config = {"latest": 1}
    mock_source = make_mock_source(
        mock_entrypoint_read,
        iter(
            any_request_and_response_with_a_record()
            + [
                # here, we test that even if messages are emitted in a different order, we still rely on `emitted_at`
                connector_configuration_control_message(latest, latest_config),
                connector_configuration_control_message(earliest, earliest_config),
            ]
        ),
    )
    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    stream_read: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.latest_config_update == latest_config


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_given_multiple_control_messages_with_same_timestamp_then_stream_read_has_latest_based_on_message_order(
    mock_entrypoint_read: Mock,
) -> None:
    emitted_at = 0
    earliest_config = {"earliest": 0}
    latest_config = {"latest": 1}
    mock_source = make_mock_source(
        mock_entrypoint_read,
        iter(
            any_request_and_response_with_a_record()
            + [
                connector_configuration_control_message(emitted_at, earliest_config),
                connector_configuration_control_message(emitted_at, latest_config),
            ]
        ),
    )
    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    stream_read: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert stream_read.latest_config_update == latest_config


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_given_auxiliary_requests_then_return_auxiliary_request(mock_entrypoint_read: Mock) -> None:
    mock_source = make_mock_source(mock_entrypoint_read, iter(any_request_and_response_with_a_record() + [auxiliary_request_log_message()]))
    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    stream_read: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert len(stream_read.auxiliary_requests) == 1


@patch("airbyte_cdk.connector_builder.message_grouper.AirbyteEntrypoint.read")
def test_given_no_slices_then_return_empty_slices(mock_entrypoint_read: Mock) -> None:
    mock_source = make_mock_source(mock_entrypoint_read, iter([auxiliary_request_log_message()]))
    connector_builder_handler = MessageGrouper(MAX_PAGES_PER_SLICE, MAX_SLICES)
    stream_read: StreamRead = connector_builder_handler.get_message_groups(
        source=mock_source, config=CONFIG, configured_catalog=create_configured_catalog("hashiras")
    )

    assert len(stream_read.slices) == 0


def make_mock_source(mock_entrypoint_read: Mock, return_value: Iterator[AirbyteMessage]) -> MagicMock:
    mock_source = MagicMock()
    mock_entrypoint_read.return_value = return_value
    return mock_source


def request_log_message(request: Mapping[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"request:{json.dumps(request)}"))


def response_log_message(response: Mapping[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"response:{json.dumps(response)}"))


def record_message(stream: str, data: Mapping[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=1234))


def slice_message(slice_descriptor: str = '{"key": "value"}') -> AirbyteMessage:
    return AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message="slice:" + slice_descriptor))


def connector_configuration_control_message(emitted_at: float, config: Mapping[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(
        type=MessageType.CONTROL,
        control=AirbyteControlMessage(
            type=OrchestratorType.CONNECTOR_CONFIG,
            emitted_at=emitted_at,
            connectorConfig=AirbyteControlConnectorConfigMessage(config=config),
        ),
    )


def auxiliary_request_log_message() -> AirbyteMessage:
    return AirbyteMessage(
        type=MessageType.LOG,
        log=AirbyteLogMessage(
            level=Level.INFO,
            message=json.dumps(
                {
                    "http": {
                        "is_auxiliary": True,
                        "title": "a title",
                        "description": "a description",
                        "request": {},
                        "response": {},
                    },
                    "url": {"full": "https://a-url.com"},
                }
            ),
        ),
    )


def request_response_log_message(request: Mapping[str, Any], response: Mapping[str, Any], url: str) -> AirbyteMessage:
    return AirbyteMessage(
        type=MessageType.LOG,
        log=AirbyteLogMessage(
            level=Level.INFO,
            message=json.dumps(
                {
                    "airbyte_cdk": {"stream": {"name": "a stream name"}},
                    "http": {"title": "a title", "description": "a description", "request": request, "response": response},
                    "url": {"full": url},
                }
            ),
        ),
    )


def any_request_and_response_with_a_record() -> List[AirbyteMessage]:
    return [
        request_response_log_message({"request": 1}, {"response": 2}, "http://any_url.com"),
        record_message("hashiras", {"name": "Shinobu Kocho"}),
    ]
