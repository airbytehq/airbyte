#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import logging
from datetime import timedelta
from unittest.mock import MagicMock

import requests
from source_marketo.source import SourceMarketo

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream

from .conftest import START_DATE, get_stream_by_name


def _make_response(json_data):
    """Create a real requests.Response so CDK decoders can process it."""
    resp = requests.Response()
    resp.status_code = 200
    resp._content = json.dumps(json_data).encode("utf-8")
    resp.headers["Content-Type"] = "application/json"
    return resp


logger = logging.getLogger("airbyte")


def test_parse_response_incremental(config, requests_mock):
    """Campaigns stream returns all records from the API response.
    Client-side incremental filtering is handled by the CDK framework at the
    source level, not at the stream.read_records level."""
    created_at_record_1 = (START_DATE + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    created_at_record_2 = (START_DATE + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    response = {"result": [{"id": "1", "createdAt": created_at_record_1}, {"id": "2", "createdAt": created_at_record_2}]}
    requests_mock.get("/rest/v1/campaigns.json", json=response)

    stream = get_stream_by_name("campaigns", config)
    records = []
    for stream_slice in stream.stream_slices(sync_mode=SyncMode.incremental):
        for record in stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice):
            records.append(dict(record))
    assert len(records) == 2
    assert records[0]["id"] == "1"
    assert records[1]["id"] == "2"


def test_source_streams(config, activity, requests_mock):
    source = SourceMarketo()
    requests_mock.get("/rest/v1/activities/types.json", json={"result": [activity]})
    streams = source.streams(config)

    # 7 declarative streams (activity_types, segmentations, campaigns, lists, programs, emails, program_tokens)
    # + 1 bulk export stream (leads)
    # + 1 dynamic activity stream (activities_send_email)
    assert len(streams) == 9
    assert all(isinstance(stream, DeclarativeStream) for stream in streams)


def test_programs_normalize_datetime(config, requests_mock):
    created_at = (START_DATE + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    updated_at = (START_DATE + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    requests_mock.get(
        "/rest/asset/v1/programs.json",
        json={"result": [{"createdAt": f"{created_at}+0000", "updatedAt": f"{updated_at}+0000"}]},
    )

    stream = get_stream_by_name("programs", config)
    stream_slice = stream.stream_slices(sync_mode=SyncMode.full_refresh)[0]
    record = next(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))

    assert dict(record) == {"createdAt": created_at, "updatedAt": updated_at}


def test_programs_next_page_token(config):
    page_size = 200
    records = [{"id": i} for i in range(page_size)]
    last_record = {"id": page_size - 1}
    response = _make_response({"result": records})
    stream = get_stream_by_name("programs", config)
    assert stream.retriever.paginator.pagination_strategy.next_page_token(
        response, len(records), last_record, last_page_token_value=None
    ) == page_size


def test_segmentations_next_page_token(config):
    page_size = 200
    records = [{"id": i} for i in range(page_size)]
    last_record = {"id": page_size - 1}
    response = _make_response({"result": records})
    stream = get_stream_by_name("segmentations", config)
    assert stream.retriever.paginator.pagination_strategy.next_page_token(
        response, len(records), last_record, last_page_token_value=None
    ) == page_size
