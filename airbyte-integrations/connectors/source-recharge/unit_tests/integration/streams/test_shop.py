#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from unittest import TestCase

import freezegun
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template

from ..config import NOW
from ..request_builder import get_stream_request
from ..utils import config, read_full_refresh

_STREAM_NAME = "shop"


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh(TestCase):
    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        template = find_template("shop", __file__)
        http_mocker.get(get_stream_request(_STREAM_NAME, "2021-01", False).build(), HttpResponse(json.dumps(template), 200))
        output = read_full_refresh(config(), _STREAM_NAME)
        assert len(output.records) == 1
