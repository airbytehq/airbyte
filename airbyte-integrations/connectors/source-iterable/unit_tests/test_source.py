#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import math
from unittest import mock

import freezegun
import pendulum
import pytest
import responses
from source_iterable.iterable_streams import RangeSliceGenerator
from source_iterable.source import SourceIterable


@pytest.fixture
def response_mock():
    with responses.RequestsMock() as resp_mock:
        record_js = {"profileUpdatedAt": "2020"}
        resp_body = "\n".join([json.dumps(record_js)])
        responses.add("GET", "https://api.iterable.com/api/export/data.json", body=resp_body)
        yield resp_mock


@responses.activate
@freezegun.freeze_time("2021-01-01")
@pytest.mark.parametrize("catalog", (["users"]), indirect=True)
def test_stream_correct(response_mock, catalog):
    TEST_START_DATE = "2020"
    chunks = math.ceil((pendulum.today() - pendulum.parse(TEST_START_DATE)).days / RangeSliceGenerator.RANGE_LENGTH_DAYS)
    source = SourceIterable()
    records = list(
        source.read(
            mock.MagicMock(),
            {"start_date": TEST_START_DATE, "api_key": "api_key"},
            catalog,
            None,
        )
    )
    assert len(records) == chunks
