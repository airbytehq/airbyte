#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.logger import AirbyteLogger
from source_sendgrid.created_expected_records import transform_record_to_expected_record
from source_sendgrid.source import SourceSendgrid
from source_sendgrid.streams import SendgridStream


@pytest.fixture(name="sendgrid_stream")
def sendgrid_stream_fixture(mocker) -> SendgridStream:
    # Wipe the internal list of abstract methods to allow instantiating the abstract class without implementing its abstract methods
    mocker.patch("source_sendgrid.streams.SendgridStream.__abstractmethods__", set())
    # Mypy yells at us because we're init'ing an abstract class
    return SendgridStream()  # type: ignore


def test_parse_response_gracefully_handles_nulls(mocker, sendgrid_stream: SendgridStream):
    response = requests.Response()
    mocker.patch.object(response, "json", return_value=None)
    mocker.patch.object(response, "request", return_value=MagicMock())
    assert [] == list(sendgrid_stream.parse_response(response))


def test_source_wrong_credentials():
    source = SourceSendgrid()
    status, error = source.check_connection(logger=AirbyteLogger(), config={"apikey": "wrong.api.key123"})
    assert not status


def clean_record(record):
    record.pop("emitted_at")
    record["data"].pop("created")
    return record


def test():
    expected_record = json.loads(
        """
    {"stream": "bounces", "data": {"created": 1621439283, "email": "vadym.hevlich@zazmic_com", "reason": "Invalid Domain", "status": ""}, "emitted_at": 1631093396000}
    """
    )
    output_record = json.loads(
        """
    {"_airbyte_ab_id":"f0d9d68e-31e4-4d5f-98c3-8ab3eb4c9035","_airbyte_emitted_at":1651771916000,"_airbyte_data":{"created":1621439283,"email":"vadym.hevlich@zazmic_com","reason":"Invalid Domain","status":""}}
    """
    )
    converted_record = transform_record_to_expected_record(output_record, "bounces")

    assert clean_record(expected_record) == clean_record(converted_record)
