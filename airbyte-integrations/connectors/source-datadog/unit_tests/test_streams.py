#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock, patch

import pytest
import requests
import requests_mock as req_mock
from airbyte_cdk.models import SyncMode
from source_datadog.source import SourceDatadog
from source_datadog.streams import (
    AuditLogs,
    Dashboards,
    DatadogStream,
    Downtimes,
    Incidents,
    IncidentTeams,
    Logs,
    Metrics,
    SyntheticTests,
    Users,
)


@pytest.mark.parametrize(
    "stream",
    [AuditLogs, Dashboards, Downtimes, Incidents, IncidentTeams, Logs, Metrics, SyntheticTests, Users],
)
def test_task_stream(requests_mock, stream, config, mock_responses):
    requests_mock.get(req_mock.ANY, json=mock_responses.get(stream.__name__))
    requests_mock.post(req_mock.ANY, json=mock_responses.get(stream.__name__))
    args = SourceDatadog().connector_config(config)
    instance = stream(**args)

    stream_slice = instance.stream_slices(sync_mode=SyncMode.full_refresh)
    record = next(instance.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))

    assert record


@patch.multiple(DatadogStream, __abstractmethods__=set())
def test_next_page_token(config):
    stream = DatadogStream(
        query=config["query"],
        max_records_per_request=config["max_records_per_request"],
        start_date=config["start_date"],
        end_date=config["end_date"],
    )
    inputs = {"response": MagicMock()}
    assert stream.next_page_token(**inputs) is None


@pytest.mark.parametrize(
    "stream",
    [AuditLogs, Dashboards, Downtimes, Incidents, IncidentTeams, Logs, Metrics, SyntheticTests, Users],
)
def test_next_page_token_empty_response(stream, config):
    expected_token = None
    args = SourceDatadog().connector_config(config)
    instance = stream(**args)
    response = requests.Response()
    response._content = json.dumps({}).encode("utf-8")
    assert instance.next_page_token(response=response) == expected_token


@pytest.mark.parametrize(
    "stream",
    [AuditLogs, Logs],
)
def test_next_page_token_inc(stream, config):
    args = SourceDatadog().connector_config(config)
    instance = stream(**args)
    response = requests.Response()
    body_content = {"meta": {"page": {"after": "test_cursor"}}}
    response._content = json.dumps(body_content).encode("utf-8")
    result = instance.next_page_token(response=response)
    assert result.get("page").get("cursor") == "test_cursor"


@pytest.mark.parametrize(
    "stream",
    [Incidents, IncidentTeams],
)
def test_next_page_token_paginated(stream, config):
    args = SourceDatadog().connector_config(config)
    instance = stream(**args)
    response = requests.Response()
    body_content = {
        "meta": {
            "pagination": {
                "offset": 998,
                "next_offset": 999,
            }
        }
    }
    response._content = json.dumps(body_content).encode("utf-8")
    result = instance.next_page_token(response=response)
    assert result.get("offset") == 999
