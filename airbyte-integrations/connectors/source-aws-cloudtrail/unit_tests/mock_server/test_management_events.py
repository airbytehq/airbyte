# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStateMessageSerializer, SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("lookup_filter", [None, {"attribute_key": "EventName", "attribute_value": "CreateTrail"}])
@freeze_time("2024-10-02T00:00:00Z")
def test_incremental_read_signs_requests_paginates_and_resumes(source_factory, lookup_filter: dict | None) -> None:
    config = {
        "aws_key_id": "test-key",
        "aws_secret_key": "test-secret",
        "aws_region_name": "us-east-1",
        "start_date": "2024-10-01",
    }
    if lookup_filter:
        config["lookup_attributes_filter"] = lookup_filter
    catalog = CatalogBuilder().with_stream("management_events", SyncMode.incremental).build()
    body = {"MaxResults": 50, "StartTime": 1727740800, "EndTime": 1727827200}
    if lookup_filter:
        body["LookupAttributes"] = [{"AttributeKey": "EventName", "AttributeValue": "CreateTrail"}]

    def request(payload: dict) -> HttpRequest:
        return HttpRequest("https://cloudtrail.us-east-1.amazonaws.com/", body=payload)

    def response(events: list, token: str | None = None) -> HttpResponse:
        payload = {"Events": events}
        if token:
            payload["NextToken"] = token
        return HttpResponse(json.dumps(payload))

    with HttpMocker() as mocker:
        first = request(body)
        second = request({**body, "NextToken": "page-2"})
        mocker.post(first, response([{"EventId": "first", "EventTime": 1727744400}], "page-2"))
        mocker.post(second, response([{"EventId": "second", "EventTime": 1727748000}]))
        source = source_factory(config, catalog, [])
        list(source.read(logging.getLogger("test"), config, catalog, state=[]))
        mocker.assert_number_of_calls(first, 1)
        mocker.assert_number_of_calls(second, 1)

        resumed = request({**body, "StartTime": 1727748000})
        mocker.post(resumed, response([]))
        state = AirbyteStateMessageSerializer.load(
            {
                "type": "STREAM",
                "stream": {"stream_descriptor": {"name": "management_events"}, "stream_state": {"EventTime": "1727748000"}},
            }
        )
        source = source_factory(config, catalog, [state])
        resumed_messages = list(source.read(logging.getLogger("test"), config, catalog, state=[state]))
        final_state = [message.state for message in resumed_messages if message.type == Type.STATE][-1]
        assert AirbyteStateMessageSerializer.dump(final_state) == {
            "type": "STREAM",
            "stream": {"stream_descriptor": {"name": "management_events"}, "stream_state": {"EventTime": "1727748000"}},
        }
        mocker.assert_number_of_calls(resumed, 1)
        history = mocker._mocker.request_history
        assert len(history) == 3
        for outgoing in history:
            payload = outgoing.json()
            assert type(payload["StartTime"]) is int
            assert type(payload["EndTime"]) is int
            assert outgoing.headers["Authorization"].startswith(
                "AWS4-HMAC-SHA256 Credential=test-key/20241002/us-east-1/cloudtrail/aws4_request, "
            )
            assert outgoing.headers["X-Amz-Date"] == "20241002T000000Z"
            assert outgoing.headers["x-amz-target"] == "com.amazonaws.cloudtrail.v20131101.CloudTrail_20131101.LookupEvents"
            assert outgoing.headers["Content-Type"] == "application/x-amz-json-1.1"
