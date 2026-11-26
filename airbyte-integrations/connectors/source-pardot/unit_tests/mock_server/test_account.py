# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import AirbyteStreamStatus
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response
from .utils import read_stream


_STREAM = "account"
_PATH = "v5/objects/account"
_FIELDS = (
    "id,company,level,website,pluginCampaignId,addressOne,addressTwo,city,state,zip,territory,country,phone,fax,adminId,"
    "maximumDailyApiCalls,apiCallsUsed,createdAt,updatedAt,createdById,updatedById"
)
_ACCOUNT = {
    "id": 1001,
    "company": "Example Inc",
    "level": "Advanced",
    "website": "https://www.example.com",
    "pluginCampaignId": 5,
    "addressOne": "1 Example Street",
    "city": "Springfield",
    "country": "United States",
    "adminId": 11,
    "maximumDailyApiCalls": 100000,
    "apiCallsUsed": 1200,
    "createdAt": "2026-02-01T08:00:00-08:00",
    "updatedAt": "2026-03-01T09:00:00-08:00",
    "createdById": 11,
    "updatedById": 11,
}


class TestAccountStream(TestCase):
    @HttpMocker()
    def test_reads_the_one_account(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            PardotRequestBuilder.endpoint(_PATH).with_query_param("fields", _FIELDS).build(),
            HttpResponse(body=json.dumps(_ACCOUNT), status_code=200),
        )

        output = read_stream(_STREAM)

        assert [message.record.data for message in output.records] == [_ACCOUNT]
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
