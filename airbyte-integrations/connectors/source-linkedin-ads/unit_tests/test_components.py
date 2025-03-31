#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from requests import Response, Session
from requests.models import PreparedRequest
from source_linkedin_ads.components import (
    AnalyticsDatetimeBasedCursor,
    LinkedInAdsCustomRetriever,
    LinkedInAdsRecordExtractor,
    SafeEncodeHttpRequester,
    SafeHttpClient,
    StreamSlice,
)


logger = logging.getLogger("airbyte")


@pytest.fixture
def mock_response():
    response = MagicMock(spec=Response)
    response.json.return_value = {
        "elements": [
            {"lastModified": "2024-09-01T00:00:00Z", "created": "2024-08-01T00:00:00Z", "data": "value1"},
            {"lastModified": "2024-09-02T00:00:00Z", "created": "2024-08-02T00:00:00Z", "data": "value2"},
        ]
    }
    return response


@pytest.fixture
def mock_analytics_cursor_params():
    return {
        "start_datetime": MagicMock(),
        "cursor_field": MagicMock(),
        "datetime_format": "%s",
        "config": MagicMock(),
        "parameters": MagicMock(),
    }


@pytest.fixture
def mock_retriever_params():
    return {"requester": MagicMock(), "record_selector": MagicMock(), "config": MagicMock(), "parameters": MagicMock()}


def test_safe_http_client_create_prepared_request():
    client = SafeHttpClient(name="test_client", logger=logger)

    http_method = "GET"
    url = "http://example.com"
    params = {"key1": "value1", "key2": "value2"}

    prepared_request = client._create_prepared_request(
        http_method=http_method,
        url=url,
        params=params,
    )

    assert isinstance(prepared_request, PreparedRequest)
    assert "key1=value1&key2=value2" in prepared_request.url


def test_safe_encode_http_requester_post_init():
    parameters = {"param1": "value1"}
    requester = SafeEncodeHttpRequester(
        name="test_requester",
        url_base="http://example.com",
        path="test/path",
        http_method="GET",
        parameters=parameters,
        config={},
    )

    assert requester._http_client is not None
    assert isinstance(requester._http_client, SafeHttpClient)


def test_analytics_datetime_based_cursor_chunk_analytics_fields(mock_analytics_cursor_params):
    cursor = AnalyticsDatetimeBasedCursor(**mock_analytics_cursor_params)
    chunks = list(cursor.chunk_analytics_fields(fields=["field1", "field2", "field3"], fields_chunk_size=2))

    assert len(chunks) == 2
    for chunk in chunks:
        assert "dateRange" in chunk and "pivotValues" in chunk


def test_analytics_datetime_based_cursor_partition_daterange(mock_analytics_cursor_params):
    cursor = AnalyticsDatetimeBasedCursor(**mock_analytics_cursor_params)
    start = datetime(2024, 9, 1)
    end = datetime(2024, 9, 5)
    step = timedelta(days=2)

    slices = cursor._partition_daterange(start=start, end=end, step=step)

    assert len(slices) == 3
    for slice_ in slices:
        assert "field_date_chunks" in slice_.cursor_slice


def test_linkedin_ads_record_extractor_extract_records(mock_response):
    extractor = LinkedInAdsRecordExtractor()
    records = list(extractor.extract_records(response=mock_response))

    assert len(records) == 2
    for record in records:
        assert "lastModified" in record
        assert "created" in record


def test_linkedin_ads_custom_retriever_stream_slices(mock_retriever_params):
    retriever = LinkedInAdsCustomRetriever(**mock_retriever_params)
    slices = list(retriever.stream_slices())

    assert len(slices) > 0


def test_linkedin_ads_custom_retriever_read_records(mock_response, mock_retriever_params):
    retriever = LinkedInAdsCustomRetriever(**mock_retriever_params)

    retriever._apply_transformations = MagicMock()
    retriever.stream_slicer = MagicMock()
    retriever.stream_slicer.stream_slices = MagicMock(return_value=[StreamSlice(partition={}, cursor_slice={})])
    retriever.read_records = MagicMock(return_value=mock_response.json()["elements"])

    records = list(retriever.read_records(records_schema={}, stream_slice=StreamSlice(partition={}, cursor_slice={})))

    assert len(records) == 2
    for record in records:
        assert "data" in record
