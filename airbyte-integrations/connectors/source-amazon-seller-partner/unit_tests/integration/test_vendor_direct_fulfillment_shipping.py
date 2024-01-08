#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


class FullRefreshTest(TestCase):
    def test_read(self, http_mocker: HttpMocker) -> None:
        assert True
