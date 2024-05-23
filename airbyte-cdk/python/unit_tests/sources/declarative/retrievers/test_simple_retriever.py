#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, SyncMode, Type
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor, DeclarativeCursor, ResumableFullRefreshCursor
from airbyte_cdk.sources.declarative.partition_routers import SinglePartitionRouter
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import CursorPaginationStrategy, PageIncrement
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever, SimpleRetrieverTestReadDecorator
from airbyte_cdk.sources.types import Record

A_SLICE_STATE = {"slice_state": "slice state value"}
A_STREAM_SLICE = {"stream slice": "slice value"}
A_STREAM_STATE = {"stream state": "state value"}

primary_key = "pk"
records = [{"id": 1}, {"id": 2}]
request_response_logs = [
    AirbyteLogMessage(level=Level.INFO, message="request:{}"),
    AirbyteLogMessage(level=Level.INFO, message="response{}"),
]
config = {}


@patch.object(SimpleRetriever, "_read_pages", return_value=iter([]))
def test_simple_retriever_full(mock_http_stream):
    requester = MagicMock()
    request_params = {"param": "value"}
    requester.get_request_params.return_value = request_params

    paginator = MagicMock()
    next_page_token = {"cursor": "cursor_value"}
    paginator.path.return_value = None
    paginator.next_page_token.return_value = next_page_token
    paginator.get_requesyyt_headers.return_value = {}

    record_selector = MagicMock()
    record_selector.select_records.return_value = records

    cursor = MagicMock(spec=DeclarativeCursor)
    stream_slices = [{"date": "2022-01-01"}, {"date": "2022-01-02"}]
    cursor.stream_slices.return_value = stream_slices

    response = requests.Response()
    response.status_code = 200

    underlying_state = {"date": "2021-01-01"}
    cursor.get_stream_state.return_value = underlying_state

    requester.get_authenticator.return_value = NoAuth({})
    url_base = "https://airbyte.io"
    requester.get_url_base.return_value = url_base
    path = "/v1"
    requester.get_path.return_value = path
    http_method = HttpMethod.GET
    requester.get_method.return_value = http_method
    backoff_time = 60
    should_retry = ResponseStatus.retry(backoff_time)
    requester.interpret_response_status.return_value = should_retry
    request_body_json = {"body": "json"}
    requester.request_body_json.return_value = request_body_json

    request_body_data = {"body": "data"}
    requester.get_request_body_data.return_value = request_body_data
    request_body_json = {"body": "json"}
    requester.get_request_body_json.return_value = request_body_json
    request_kwargs = {"kwarg": "value"}
    requester.request_kwargs.return_value = request_kwargs

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=cursor,
        cursor=cursor,
        parameters={},
        config={},
    )

    assert retriever.primary_key == primary_key
    assert retriever.state == underlying_state
    assert retriever._next_page_token(response) == next_page_token
    assert retriever._request_params(None, None, None) == {}
    assert retriever.stream_slices() == stream_slices

    assert retriever._last_response is None
    assert retriever._last_record is None
    assert list(retriever._parse_response(response, stream_state={}, records_schema={})) == records
    assert retriever._last_response == response
    assert retriever._last_page_size == 2

    [r for r in retriever.read_records(SyncMode.full_refresh)]
    paginator.reset.assert_called()


@patch.object(SimpleRetriever, "_read_pages", return_value=iter([*request_response_logs, *records]))
def test_simple_retriever_with_request_response_logs(mock_http_stream):
    requester = MagicMock()
    paginator = MagicMock()
    record_selector = MagicMock()
    stream_slicer = DatetimeBasedCursor(
        start_datetime="",
        end_datetime="",
        step="P1D",
        cursor_field="id",
        datetime_format="",
        cursor_granularity="P1D",
        config={},
        parameters={},
    )

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        parameters={},
        config={},
    )

    actual_messages = [r for r in retriever.read_records(SyncMode.full_refresh)]
    paginator.reset.assert_called()

    assert isinstance(actual_messages[0], AirbyteLogMessage)
    assert isinstance(actual_messages[1], AirbyteLogMessage)
    assert actual_messages[2] == records[0]
    assert actual_messages[3] == records[1]


@pytest.mark.parametrize(
    "initial_state, expected_reset_value, expected_next_page",
    [
        pytest.param(None, None, 1, id="test_initial_sync_no_state"),
        pytest.param({"next_page_token": 10}, 10, 11, id="test_reset_with_next_page_token"),
    ]
)
def test_simple_retriever_resumable_full_refresh_cursor_page_increment(initial_state, expected_reset_value, expected_next_page):
    expected_records = [
        Record(data={"id": "abc"}, associated_slice=None),
        Record(data={"id": "def"}, associated_slice=None),
        Record(data={"id": "ghi"}, associated_slice=None),
        Record(data={"id": "jkl"}, associated_slice=None),
        Record(data={"id": "mno"}, associated_slice=None),
        Record(data={"id": "123"}, associated_slice=None),
        Record(data={"id": "456"}, associated_slice=None),
        Record(data={"id": "789"}, associated_slice=None),
    ]

    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps({"data": [record.data for record in expected_records[:5]]}).encode("utf-8")

    requester = MagicMock()
    requester.send_request.side_effect = [
        response,
        response,
    ]

    record_selector = MagicMock()
    record_selector.select_records.side_effect = [
        [
            expected_records[0],
            expected_records[1],
            expected_records[2],
            expected_records[3],
            expected_records[4],
        ],
        [
            expected_records[5],
            expected_records[6],
            expected_records[7],
        ]
    ]

    page_increment_strategy = PageIncrement(config={}, page_size=5, parameters={})
    paginator = DefaultPaginator(config={}, pagination_strategy=page_increment_strategy, url_base="https://airbyte.io", parameters={})
    paginator.reset = Mock(wraps=paginator.reset)

    stream_slicer = ResumableFullRefreshCursor(parameters={})
    if initial_state:
        stream_slicer.set_initial_state(initial_state)

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        cursor=stream_slicer,
        parameters={},
        config={},
    )

    stream_slice = list(stream_slicer.stream_slices())[0]
    actual_records = [r for r in retriever.read_records(records_schema={}, stream_slice=stream_slice)]

    assert len(actual_records) == 5
    assert actual_records == expected_records[:5]
    assert retriever.state == {"next_page_token": expected_next_page}

    actual_records = [r for r in retriever.read_records(records_schema={}, stream_slice=stream_slice)]
    assert len(actual_records) == 3
    assert actual_records == expected_records[5:]
    assert retriever.state == {"__ab_full_refresh_sync_complete": True}

    paginator.reset.assert_called_once_with(reset_value=expected_reset_value)


@pytest.mark.parametrize(
    "initial_state, expected_reset_value, expected_next_page",
    [
        pytest.param(None, None, 1, id="test_initial_sync_no_state"),
        pytest.param(
            {"next_page_token": "https://for-all-mankind.nasa.com/api/v1/astronauts?next_page=tracy_stevens"},
            "https://for-all-mankind.nasa.com/api/v1/astronauts?next_page=tracy_stevens",
            "https://for-all-mankind.nasa.com/api/v1/astronauts?next_page=gordo_stevens",
            id="test_reset_with_next_page_token"
        ),
    ]
)
def test_simple_retriever_resumable_full_refresh_cursor_reset_cursor_pagination(initial_state, expected_reset_value, expected_next_page):
    expected_records = [
        Record(data={"name": "ed_baldwin"}, associated_slice=None),
        Record(data={"name": "danielle_poole"}, associated_slice=None),
        Record(data={"name": "tracy_stevens"}, associated_slice=None),
        Record(data={"name": "deke_slayton"}, associated_slice=None),
        Record(data={"name": "molly_cobb"}, associated_slice=None),
        Record(data={"name": "gordo_stevens"}, associated_slice=None),
        Record(data={"name": "margo_madison"}, associated_slice=None),
        Record(data={"name": "ellen_waverly"}, associated_slice=None),
    ]

    response_1 = requests.Response()
    response_1.status_code = 200
    response_body = {
        "data": [r.data for r in expected_records[:5]],
        "next_page": "https://for-all-mankind.nasa.com/api/v1/astronauts?next_page=gordo_stevens"
    }
    response_1._content = json.dumps(response_body).encode("utf-8")
    response_2 = requests.Response()
    response_2.status_code = 200
    response_body = {
        "data": [r.data for r in expected_records[5:]],
    }
    response_2._content = json.dumps(response_body).encode("utf-8")

    requester = MagicMock()
    requester.send_request.side_effect = [
        response_1,
        response_2,
    ]

    record_selector = MagicMock()
    record_selector.select_records.side_effect = [
        [
            expected_records[0],
            expected_records[1],
            expected_records[2],
            expected_records[3],
            expected_records[4],
        ],
        [
            expected_records[5],
            expected_records[6],
            expected_records[7],
        ]
    ]

    cursor_pagination_strategy = CursorPaginationStrategy(config={}, cursor_value="{{ response.next_page }}", parameters={})
    paginator = DefaultPaginator(config={}, pagination_strategy=cursor_pagination_strategy, url_base="https://for-all-mankind.nasa.com/api/v1", parameters={})
    paginator.reset = Mock(wraps=paginator.reset)

    stream_slicer = ResumableFullRefreshCursor(parameters={})
    if initial_state:
        stream_slicer.set_initial_state(initial_state)

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        cursor=stream_slicer,
        parameters={},
        config={},
    )

    stream_slice = list(stream_slicer.stream_slices())[0]
    actual_records = [r for r in retriever.read_records(records_schema={}, stream_slice=stream_slice)]

    assert len(actual_records) == 5
    assert actual_records == expected_records[:5]
    assert retriever.state == {"next_page_token": "https://for-all-mankind.nasa.com/api/v1/astronauts?next_page=gordo_stevens"}

    actual_records = [r for r in retriever.read_records(records_schema={}, stream_slice=stream_slice)]
    assert len(actual_records) == 3
    assert actual_records == expected_records[5:]
    assert retriever.state == {"__ab_full_refresh_sync_complete": True}

    paginator.reset.assert_called_once_with(reset_value=expected_reset_value)


def test_simple_retriever_resumable_full_refresh_cursor_reset_skip_completed_stream():
    expected_records = [
        Record(data={"id": "abc"}, associated_slice=None),
        Record(data={"id": "def"}, associated_slice=None),
    ]

    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps({}).encode("utf-8")

    requester = MagicMock()
    requester.send_request.side_effect = [
        response,
    ]

    record_selector = MagicMock()
    record_selector.select_records.return_value = [expected_records[0],expected_records[1],]

    page_increment_strategy = PageIncrement(config={}, page_size=5, parameters={})
    paginator = DefaultPaginator(config={}, pagination_strategy=page_increment_strategy, url_base="https://airbyte.io", parameters={})
    paginator.reset = Mock(wraps=paginator.reset)

    stream_slicer = ResumableFullRefreshCursor(parameters={})
    stream_slicer.set_initial_state({"__ab_full_refresh_sync_complete": True})

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        cursor=stream_slicer,
        parameters={},
        config={},
    )

    stream_slice = list(stream_slicer.stream_slices())[0]
    actual_records = [r for r in retriever.read_records(records_schema={}, stream_slice=stream_slice)]

    assert len(actual_records) == 0
    assert retriever.state == {"__ab_full_refresh_sync_complete": True}

    paginator.reset.assert_not_called()


@pytest.mark.parametrize(
    "test_name, paginator_mapping, stream_slicer_mapping, expected_mapping",
    [
        ("test_empty_headers", {}, {}, {}),
        ("test_header_from_pagination_and_slicer", {"offset": 1000}, {"key": "value"}, {"key": "value", "offset": 1000}),
        ("test_header_from_stream_slicer", {}, {"slice": "slice_value"}, {"slice": "slice_value"}),
        ("test_duplicate_header_slicer_paginator", {"k": "v"}, {"k": "slice_value"}, None),
    ],
)
def test_get_request_options_from_pagination(test_name, paginator_mapping, stream_slicer_mapping, expected_mapping):
    # This test does not test request headers because they must be strings
    paginator = MagicMock()
    paginator.get_request_params.return_value = paginator_mapping
    paginator.get_request_body_data.return_value = paginator_mapping
    paginator.get_request_body_json.return_value = paginator_mapping

    stream_slicer = MagicMock()
    stream_slicer.get_request_params.return_value = stream_slicer_mapping
    stream_slicer.get_request_body_data.return_value = stream_slicer_mapping
    stream_slicer.get_request_body_json.return_value = stream_slicer_mapping

    record_selector = MagicMock()
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=MagicMock(),
        record_selector=record_selector,
        paginator=paginator,
        stream_slicer=stream_slicer,
        parameters={},
        config={},
    )

    request_option_type_to_method = {
        RequestOptionType.request_parameter: retriever._request_params,
        RequestOptionType.body_data: retriever._request_body_data,
        RequestOptionType.body_json: retriever._request_body_json,
    }

    for _, method in request_option_type_to_method.items():
        if expected_mapping is not None:
            actual_mapping = method(None, None, None)
            assert actual_mapping == expected_mapping
        else:
            try:
                method(None, None, None)
                assert False
            except ValueError:
                pass


@pytest.mark.parametrize(
    "test_name, paginator_mapping, expected_mapping",
    [
        ("test_only_base_headers", {}, {"key": "value"}),
        ("test_header_from_pagination", {"offset": 1000}, {"key": "value", "offset": "1000"}),
        ("test_duplicate_header", {"key": 1000}, None),
    ],
)
def test_get_request_headers(test_name, paginator_mapping, expected_mapping):
    # This test is separate from the other request options because request headers must be strings
    paginator = MagicMock()
    paginator.get_request_headers.return_value = paginator_mapping
    requester = MagicMock(use_cache=False)

    stream_slicer = MagicMock()
    stream_slicer.get_request_headers.return_value = {"key": "value"}

    record_selector = MagicMock()
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        paginator=paginator,
        parameters={},
        config={},
    )

    request_option_type_to_method = {
        RequestOptionType.header: retriever._request_headers,
    }

    for _, method in request_option_type_to_method.items():
        if expected_mapping:
            actual_mapping = method(None, None, None)
            assert actual_mapping == expected_mapping
        else:
            try:
                method(None, None, None)
                assert False
            except ValueError:
                pass


@pytest.mark.parametrize(
    "test_name, paginator_mapping, ignore_stream_slicer_parameters_on_paginated_requests, next_page_token, expected_mapping",
    [
        ("test_do_not_ignore_stream_slicer_params_if_ignore_is_true_but_no_next_page_token", {"key_from_pagination": "1000"}, True, None, {"key_from_pagination": "1000"}),
        ("test_do_not_ignore_stream_slicer_params_if_ignore_is_false_and_no_next_page_token", {"key_from_pagination": "1000"}, False, None, {"key_from_pagination": "1000", "key_from_slicer": "value"}),
        ("test_ignore_stream_slicer_params_on_paginated_request", {"key_from_pagination": "1000"}, True, {"page": 2}, {"key_from_pagination": "1000"}),
        ("test_do_not_ignore_stream_slicer_params_on_paginated_request", {"key_from_pagination": "1000"}, False, {"page": 2}, {"key_from_pagination": "1000", "key_from_slicer": "value"}),
    ],
)
def test_ignore_stream_slicer_parameters_on_paginated_requests(test_name, paginator_mapping, ignore_stream_slicer_parameters_on_paginated_requests, next_page_token, expected_mapping):
    # This test is separate from the other request options because request headers must be strings
    paginator = MagicMock()
    paginator.get_request_headers.return_value = paginator_mapping
    requester = MagicMock(use_cache=False)

    stream_slicer = MagicMock()
    stream_slicer.get_request_headers.return_value = {"key_from_slicer": "value"}

    record_selector = MagicMock()
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        record_selector=record_selector,
        stream_slicer=stream_slicer,
        paginator=paginator,
        ignore_stream_slicer_parameters_on_paginated_requests=ignore_stream_slicer_parameters_on_paginated_requests,
        parameters={},
        config={},
    )

    request_option_type_to_method = {
        RequestOptionType.header: retriever._request_headers,
    }

    for _, method in request_option_type_to_method.items():
        actual_mapping = method(None, None, next_page_token={"next_page_token": "1000"})
        assert actual_mapping == expected_mapping


@pytest.mark.parametrize(
    "test_name, slicer_body_data, paginator_body_data, expected_body_data",
    [
        ("test_only_slicer_mapping", {"key": "value"}, {}, {"key": "value"}),
        ("test_only_slicer_string", "key=value", {}, "key=value"),
        ("test_slicer_mapping_and_paginator_no_duplicate", {"key": "value"}, {"offset": 1000}, {"key": "value", "offset": 1000}),
        ("test_slicer_mapping_and_paginator_with_duplicate", {"key": "value"}, {"key": 1000}, None),
        ("test_slicer_string_and_paginator", "key=value", {"offset": 1000}, None),
    ],
)
def test_request_body_data(test_name, slicer_body_data, paginator_body_data, expected_body_data):
    paginator = MagicMock()
    paginator.get_request_body_data.return_value = paginator_body_data
    requester = MagicMock(use_cache=False)

    stream_slicer = MagicMock()
    stream_slicer.get_request_body_data.return_value = slicer_body_data

    record_selector = MagicMock()
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        record_selector=record_selector,
        paginator=paginator,
        stream_slicer=stream_slicer,
        parameters={},
        config={},
    )

    if expected_body_data:
        actual_body_data = retriever._request_body_data(None, None, None)
        assert actual_body_data == expected_body_data
    else:
        try:
            retriever._request_body_data(None, None, None)
            assert False
        except ValueError:
            pass


@pytest.mark.parametrize(
    "test_name, requester_path, paginator_path, expected_path",
    [
        ("test_path_from_requester", "/v1/path", None, None),
        ("test_path_from_paginator", "/v1/path/", "/v2/paginator", "/v2/paginator"),
    ],
)
def test_path(test_name, requester_path, paginator_path, expected_path):
    paginator = MagicMock()
    paginator.path.return_value = paginator_path
    requester = MagicMock(use_cache=False)

    requester.get_path.return_value = requester_path

    record_selector = MagicMock()
    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        record_selector=record_selector,
        paginator=paginator,
        parameters={},
        config={},
    )

    actual_path = retriever._paginator_path()
    assert actual_path == expected_path


def test_limit_stream_slices():
    maximum_number_of_slices = 4
    stream_slicer = MagicMock()
    stream_slicer.stream_slices.return_value = _generate_slices(maximum_number_of_slices * 2)
    retriever = SimpleRetrieverTestReadDecorator(
        name="stream_name",
        primary_key=primary_key,
        requester=MagicMock(),
        paginator=MagicMock(),
        record_selector=MagicMock(),
        stream_slicer=stream_slicer,
        maximum_number_of_slices=maximum_number_of_slices,
        parameters={},
        config={},
    )

    truncated_slices = list(retriever.stream_slices())

    assert truncated_slices == _generate_slices(maximum_number_of_slices)


@pytest.mark.parametrize(
    "test_name, first_greater_than_second",
    [
        ("test_first_greater_than_second", True),
        ("test_second_greater_than_first", False),
    ],
)
def test_when_read_records_then_cursor_close_slice_with_greater_record(test_name, first_greater_than_second):
    first_record = Record({"first": 1}, {})
    second_record = Record({"second": 2}, {})
    records = [first_record, second_record]
    record_selector = MagicMock()
    record_selector.select_records.return_value = records
    cursor = MagicMock(spec=DeclarativeCursor)
    cursor.is_greater_than_or_equal.return_value = first_greater_than_second
    paginator = MagicMock()
    paginator.get_request_headers.return_value = {}

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=MagicMock(),
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=cursor,
        cursor=cursor,
        parameters={},
        config={},
    )
    stream_slice = {"repository": "airbyte"}

    def retriever_read_pages(_, __, ___):
        return retriever._parse_records(response=MagicMock(), stream_state={}, stream_slice=stream_slice, records_schema={})

    with patch.object(
        SimpleRetriever,
        "_read_pages",
        return_value=iter([first_record, second_record]),
        side_effect=retriever_read_pages,
    ):
        list(retriever.read_records(stream_slice=stream_slice, records_schema={}))
        cursor.close_slice.assert_called_once_with(stream_slice, first_record if first_greater_than_second else second_record)


def test_given_stream_data_is_not_record_when_read_records_then_update_slice_with_optional_record():
    stream_data = [AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="a log message"))]
    record_selector = MagicMock()
    record_selector.select_records.return_value = []
    cursor = MagicMock(spec=DeclarativeCursor)

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=MagicMock(),
        paginator=Mock(),
        record_selector=record_selector,
        stream_slicer=cursor,
        cursor=cursor,
        parameters={},
        config={},
    )
    stream_slice = {"repository": "airbyte"}

    def retriever_read_pages(_, __, ___):
        return retriever._parse_records(response=MagicMock(), stream_state={}, stream_slice=stream_slice, records_schema={})

    with patch.object(
        SimpleRetriever,
        "_read_pages",
        return_value=iter(stream_data),
        side_effect=retriever_read_pages,
    ):
        list(retriever.read_records(stream_slice=stream_slice, records_schema={}))
        cursor.observe.assert_not_called()
        cursor.close_slice.assert_called_once_with(stream_slice, None)


def _generate_slices(number_of_slices):
    return [{"date": f"2022-01-0{day + 1}"} for day in range(number_of_slices)]


@patch.object(SimpleRetriever, "_read_pages", return_value=iter([]))
def test_given_state_selector_when_read_records_use_stream_state(http_stream_read_pages, mocker):
    requester = MagicMock()
    paginator = MagicMock()
    record_selector = MagicMock()
    cursor = MagicMock(spec=DeclarativeCursor)
    cursor.select_state = MagicMock(return_value=A_SLICE_STATE)
    cursor.get_stream_state = MagicMock(return_value=A_STREAM_STATE)

    retriever = SimpleRetriever(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        paginator=paginator,
        record_selector=record_selector,
        stream_slicer=cursor,
        cursor=cursor,
        parameters={},
        config={},
    )

    list(retriever.read_records(stream_slice=A_STREAM_SLICE, records_schema={}))

    http_stream_read_pages.assert_called_once_with(mocker.ANY, A_STREAM_STATE, A_STREAM_SLICE)


def test_emit_log_request_response_messages(mocker):
    record_selector = MagicMock()
    record_selector.select_records.return_value = records

    request = requests.PreparedRequest()
    request.headers = {"header": "value"}
    request.url = "http://byrde.enterprises.com/casinos"

    response = requests.Response()
    response.request = request
    response.status_code = 200

    format_http_message_mock = mocker.patch("airbyte_cdk.sources.declarative.retrievers.simple_retriever.format_http_message")
    requester = MagicMock()
    retriever = SimpleRetrieverTestReadDecorator(
        name="stream_name",
        primary_key=primary_key,
        requester=requester,
        paginator=MagicMock(),
        record_selector=record_selector,
        stream_slicer=SinglePartitionRouter(parameters={}),
        parameters={},
        config={},
    )

    retriever._fetch_next_page(stream_state={}, stream_slice={})

    assert requester.send_request.call_args_list[0][1]["log_formatter"] is not None
    assert requester.send_request.call_args_list[0][1]["log_formatter"](response) == format_http_message_mock.return_value
