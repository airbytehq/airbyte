# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ConfigBuilder
from .monday_requests import UpdatesRequestBuilder
from .monday_requests.request_authenticators import ApiTokenAuthenticator
from .monday_responses import UpdatesResponseBuilder
from .monday_responses.records import UpdatesRecordBuilder
from .utils import read_stream


class TestUpdatesStreamFullRefresh(TestCase):
    def get_authenticator(self, config):
        return ApiTokenAuthenticator(api_token=config["credentials"]["api_token"])

    @staticmethod
    def _response(record_count: int, id_offset: int = 0):
        response = UpdatesResponseBuilder.updates_response()
        for index in range(record_count):
            response.with_record(UpdatesRecordBuilder.updates_record().with_id(f"update_{id_offset + index}"))
        return response.build()

    @HttpMocker()
    def test_read_updates_with_pagination(self, http_mocker):
        config = ConfigBuilder().with_api_token_credentials("api-token").build()
        api_token_authenticator = self.get_authenticator(config)

        http_mocker.post(
            UpdatesRequestBuilder.updates_endpoint(api_token_authenticator).build(),
            self._response(100),
        )
        http_mocker.post(
            UpdatesRequestBuilder.updates_endpoint(api_token_authenticator, page=2).build(),
            self._response(2, id_offset=100),
        )

        output = read_stream("updates", SyncMode.full_refresh, config)

        assert len(output.records) == 102
