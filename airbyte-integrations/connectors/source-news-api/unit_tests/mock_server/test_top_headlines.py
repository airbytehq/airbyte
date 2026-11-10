# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker
from unit_tests.conftest import get_source
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.contracts import StreamContracts
from unit_tests.mock_server.request_builder import build_request
from unit_tests.mock_server.response_builder import error_response


class TestTopHeadlines(StreamContracts):
    stream = "top_headlines"

    def test_check_upgrade_required(self) -> None:
        config = ConfigBuilder().build()
        with HttpMocker() as mocker:
            request = build_request(self.stream)
            mocker.get(request, error_response(426, "upgradeRequired", "Upgrade your plan."))
            output = get_source(config).check(logging.getLogger("test"), config)
            mocker.assert_number_of_calls(request, 1)
        assert output.status == Status.FAILED
        assert "News API rejected the `top_headlines` request: Upgrade your plan." in output.message
