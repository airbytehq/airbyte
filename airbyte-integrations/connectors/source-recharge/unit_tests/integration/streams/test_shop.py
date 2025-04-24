#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template

from ..config import NOW
from ..utils import StreamTestCase, read_full_refresh


_STREAM_NAME = "shop"


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh(StreamTestCase):
    _STREAM_NAME = "shop"

    @HttpMocker()
    def test_when_read_return_single_record(self, http_mocker: HttpMocker) -> None:
        template = find_template("shop", __file__)
        http_mocker.get(self.stream_request().with_old_api_version("2021-01").build(), HttpResponse(json.dumps(template), 200))
        output = read_full_refresh(self._config, _STREAM_NAME)
        assert len(output.records) == 1
