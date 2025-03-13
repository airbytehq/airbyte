# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase
from unittest.mock import patch
from typing import List

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import Level as LogLevel
from airbyte_protocol.models import SyncMode

from .config import ConfigBuilder
from .monday_requests import ItemsRequestBuilder
from .monday_requests.request_authenticators import ApiTokenAuthenticator
from .monday_responses import ErrorResponseBuilder, ItemsResponseBuilder
from .monday_responses.records import ItemsRecordBuilder
from .utils import get_log_messages_by_log_level, read_stream


class TestItemsStreamFullRefresh(TestCase):

    def get_authenticator(self, config):
        return ApiTokenAuthenticator(api_token=config["credentials"]["api_token"])

    @HttpMocker()
    def test_read_item_record(self, http_mocker):
        """
        A full refresh sync without pagination or board filtering
        """
        config = ConfigBuilder().with_api_token_credentials("api-token").build()
        api_token_authenticator = self.get_authenticator(config)
        
        http_mocker.get(
            ItemsRequestBuilder.items_endpoint(api_token_authenticator).build(),
            ItemsResponseBuilder.items_response().with_record(ItemsRecordBuilder.items_record()).build(),
        )

        output = read_stream("items", SyncMode.full_refresh, config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_read_with_board_ids_filter(self, http_mocker):
        """
        A full refresh sync with board filtering and without pagination
        """
        board_ids = [123, 456]
        config = ConfigBuilder().with_api_token_credentials("api-token").with_board_ids(board_ids).build()
        api_token_authenticator = self.get_authenticator(config)

        http_mocker.get(
            ItemsRequestBuilder.items_endpoint(api_token_authenticator, board_ids).build(),
            ItemsResponseBuilder.items_response().with_record(ItemsRecordBuilder.items_record()).build(),
        )

        output = read_stream("items", SyncMode.full_refresh, config)
        assert len(output.records) == 1
