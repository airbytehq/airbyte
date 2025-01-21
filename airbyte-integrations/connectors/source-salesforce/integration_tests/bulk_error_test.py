#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import re
from pathlib import Path
from typing import Any, Mapping

import pytest
import requests_mock
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from source_salesforce.source import SourceSalesforce

HERE = Path(__file__).parent
_ANY_CATALOG = CatalogBuilder().build()
_ANY_CONFIG = {}
_ANY_STATE = {}


@pytest.fixture(name="input_config")
def parse_input_config():
    with open(HERE.parent / "secrets/config.json", "r") as file:
        return json.loads(file.read())


@pytest.fixture(name="input_sandbox_config")
def parse_input_sandbox_config():
    with open(HERE.parent / "secrets/config_sandbox.json", "r") as file:
        return json.loads(file.read())


def get_stream(input_config: Mapping[str, Any], stream_name: str) -> Stream:
    stream_cls = type("a", (object,), {"name": stream_name})
    configured_stream_cls = type("b", (object,), {"stream": stream_cls(), "sync_mode": "full_refresh"})
    catalog_cls = type("c", (object,), {"streams": [configured_stream_cls()]})
    source = SourceSalesforce(_ANY_CATALOG, _ANY_CONFIG, _ANY_STATE)
    source.catalog = catalog_cls()
    return source.streams(input_config)[0]


def get_any_real_stream(input_config: Mapping[str, Any]) -> Stream:
    return get_stream(input_config, "ActiveFeatureLicenseMetric")


@pytest.mark.parametrize(
    "stream_name,log_messages",
    (
        (
            "Dashboard",
            ["switch to STANDARD(non-BULK) sync"],
        ),
        # CategoryNode has access limitation thus SF returns failed job statuses
        (
            "CategoryNode",
            ["insufficient access rights on cross-reference id", "switch to STANDARD(non-BULK) sync"],
        ),
    ),
    ids=["successful_switching", "failed_switching"],
)
def test_failed_jobs_with_successful_switching(caplog, input_sandbox_config, stream_name, log_messages):
    stream = get_stream(input_sandbox_config, stream_name)
    stream_slice = {"start_date": "2023-01-01T00:00:00.000+0000", "end_date": "2023-02-01T00:00:00.000+0000"}
    expected_record_ids = set(record["Id"] for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))

    create_query_matcher = re.compile(r"jobs/query$")
    job_matcher = re.compile(r"jobs/query/fake_id$")
    loaded_record_ids = []
    with requests_mock.Mocker(real_http=True) as m:
        m.register_uri(
            "POST",
            create_query_matcher,
            json={
                "id": "fake_id",
            },
        )
        m.register_uri("GET", job_matcher, json={"state": "Failed", "errorMessage": "unknown error", "id": "fake_id"})
        m.register_uri("DELETE", job_matcher, json={})
        with caplog.at_level(logging.WARNING):
            loaded_record_ids = set(
                record["Id"] for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
            )

        caplog_rec_counter = len(caplog.records) - 1
        for log_message in log_messages:
            for index in range(caplog_rec_counter, -1, -1):
                if log_message in caplog.records[index].message:
                    caplog_rec_counter = index - 1
                    break
            else:
                pytest.fail(f"{log_message} is missing from captured log")
    assert loaded_record_ids == expected_record_ids
