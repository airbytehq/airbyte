#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
import logging
from pathlib import Path
from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.streams import Stream
from source_salesforce.source import SourceSalesforce

HERE = Path(__file__).parent


@pytest.fixture(name="input_config")
def parse_input_config():
    with open(HERE.parent / "secrets/config.json", "r") as file:
        return json.loads(file.read())


def get_stream(input_config: Mapping[str, Any], stream_name: str) -> Stream:
    stream_cls = type("a", (object,), {"name": stream_name})
    configured_stream_cls = type("b", (object,), {"stream": stream_cls()})
    catalog_cls = type("c", (object,), {"streams": [configured_stream_cls()]})
    return SourceSalesforce().streams(input_config, catalog_cls())[0]


def get_any_real_stream(input_config: Mapping[str, Any]) -> Stream:
    return get_stream(input_config, "ActiveFeatureLicenseMetric")


def test_not_queryable_stream(caplog, input_config):
    stream = get_any_real_stream(input_config)
    url = f"{stream.sf_api.instance_url}/services/data/v52.0/jobs/query"

    # test non queryable BULK streams
    query = "Select Id, Subject from ActivityHistory"
    with caplog.at_level(logging.WARNING):
        assert stream.create_stream_job(query, url) is None, "this stream should be skipped"

    # check logs
    assert "is not queryable" in caplog.records[-1].message
