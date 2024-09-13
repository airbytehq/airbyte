#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
from typing import Any, List
from unittest.mock import MagicMock

import pandas as pd
import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from numpy import nan
from requests import codes
from source_sendgrid.source import SourceSendgrid

FAKE_NOW = pendulum.DateTime(2022, 1, 1, tzinfo=pendulum.timezone("utc"))
FAKE_NOW_ISO_STRING = FAKE_NOW.to_iso8601_string()

@staticmethod
def find_stream(stream_name):
    streams = SourceSendgrid().streams(config={"api_key": "wrong.api.key123"})
    # find by name
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")

@staticmethod
def record_keys_to_lowercase(records: List[StreamData]) -> List[dict[str, str | Any]]:
    return [
        {k.lower(): v if isinstance(v, str) else v for k, v in d.items()}
        for d in records
    ]


def test_source_wrong_credentials() -> None:
    source = SourceSendgrid()
    status, error = source.check_connection(logger=logging.getLogger("airbyte"), config={"api_key": "wrong.api.key123"})
    assert not status


def test_streams():
    streams = SourceSendgrid().streams(config={"api_key": "wrong.api.key123", "start_date": FAKE_NOW_ISO_STRING})
    assert len(streams) == 15


@pytest.mark.parametrize(
    "stream_name, status, expected",
    (
        ("blocks", 400, ResponseAction.RETRY),
        ("blocks", 429, ResponseAction.RETRY),
        ("suppression_group_members", 401, ResponseAction.RETRY),
    ),
)
def test_should_retry_on_permission_error(stream_name, status, expected) -> None:
    stream = find_stream(stream_name)
    response_mock = MagicMock()
    response_mock.status_code = status
    response_action = stream.retriever.requester.error_handler.interpret_response(response_mock).response_action
    assert response_action == expected


@pytest.mark.parametrize(
    "stream_name, compressed_or_decompressed_file",
    (
        ("contacts", "decompressed_response.csv"),
        ("contacts", "compressed_response"),
    ),
    ids=[
        "Decompressed response",
        "Compressed (gzipped) response",
    ]
)
def test_contact_stream_response(requests_mock, stream_name, compressed_or_decompressed_file) -> None:
    # instantiate the stream from low-code
    streams = SourceSendgrid().streams(config={"api_key": "wrong.api.key123"})
    stream = [stream for stream in streams if stream.name == stream_name][0]

    with open(os.path.dirname(__file__) + "/" + compressed_or_decompressed_file, "rb") as file_response:
        # mocking job creation requests
        url = "https://api.sendgrid.com/v3/marketing/contacts/exports"
        requests_mock.register_uri("POST", url, [{"json": {"id": "random_id"}, "status_code": 202}])

        # mocking status requests
        created_job_url = "https://api.sendgrid.com/v3/marketing/contacts/exports/random_id"
        resp_bodies = [
            {"json": {"status": "pending", "id": "random_id", "urls": []}, "status_code": 202},
            {"json": {"status": "ready", "urls": ["https://sample_url/sample_csv.csv.gzip"]}, "status_code": 202},
        ]
        requests_mock.register_uri("GET", created_job_url, resp_bodies)
        requests_mock.register_uri("GET", "https://sample_url/sample_csv.csv.gzip", [{"body": file_response, "status_code": 202}])

        # read the records
        stream_slice = next(iter(stream.stream_slices(sync_mode=SyncMode.full_refresh)))
        recs = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
        decompressed_response = pd.read_csv(os.path.dirname(__file__) + "/decompressed_response.csv", dtype=str)

        # process results
        expected_records = [
            {k.lower(): v for k, v in x.items()} 
            for x in decompressed_response.replace({nan: None}).to_dict(orient="records")
        ]
        recs = record_keys_to_lowercase(recs)
        assert recs == expected_records


def test_bad_job_response(requests_mock) -> None:
    # instantiate the stream from low-code
    streams = SourceSendgrid().streams(config={"api_key": "wrong.api.key123"})
    stream = [stream for stream in streams if stream.name == "contacts"][0]

    url = "https://api.sendgrid.com/v3/marketing/contacts/exports"

    requests_mock.register_uri(
        "POST", url, [{"json": {"errors": [{"field": "field_name", "message": "error message"}]}, "status_code": codes.BAD_REQUEST}]
    )
    with pytest.raises(Exception):
        list(stream.read_records(sync_mode=SyncMode.full_refresh))
