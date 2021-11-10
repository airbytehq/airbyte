#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
import math
from unittest import mock

import freezegun
import pendulum
import pytest
import responses
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream
from source_iterable.api import EmailSend
from source_iterable.source import SourceIterable


@pytest.fixture
def response_mock():
    with responses.RequestsMock() as resp_mock:
        record_js = {"createdAt": "2020"}
        resp_body = "\n".join([json.dumps(record_js)])
        responses.add("GET", "https://api.iterable.com/api/export/data.json", body=resp_body)
        yield resp_mock


@responses.activate
@freezegun.freeze_time("2021-01-01")
def test_stream_correct(response_mock):
    TEST_START_DATE = "2020"
    test_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="email_send", json_schema={}),
                sync_mode="full_refresh",
                destination_sync_mode="append",
            )
        ]
    )
    chunks = math.ceil((pendulum.today() - pendulum.parse(TEST_START_DATE)).days / EmailSend.RANGE_LENGTH_DAYS)

    source = SourceIterable()
    records = list(
        source.read(
            mock.MagicMock(),
            {"start_date": TEST_START_DATE, "api_key": "api_key"},
            test_catalog,
            None,
        )
    )
    assert len(records) == chunks
