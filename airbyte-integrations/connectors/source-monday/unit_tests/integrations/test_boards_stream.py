# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from unittest import TestCase

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import SyncMode

from .config import ConfigBuilder
from .monday_requests import BoardsRequestBuilder
from .monday_requests.request_authenticators import ApiTokenAuthenticator
from .monday_responses import BoardsResponseBuilder
from .monday_responses.records import BoardsRecordBuilder
from .utils import read_stream


class TestBoardsStreamFullRefresh(TestCase):
    def get_authenticator(self, config):
        return ApiTokenAuthenticator(api_token=config["credentials"]["api_token"])

    @HttpMocker()
    def test_read_board_record(self, http_mocker):
        """
        A full refresh sync of the boards stream without pagination or board filtering
        """
        config = ConfigBuilder().with_api_token_credentials("api-token").build()
        api_token_authenticator = self.get_authenticator(config)

        http_mocker.get(
            BoardsRequestBuilder.boards_endpoint(api_token_authenticator).build(),
            BoardsResponseBuilder.boards_response()
            .with_record(BoardsRecordBuilder.boards_record())
            .with_record(BoardsRecordBuilder.boards_record())
            .build(),
        )

        output = read_stream("boards", SyncMode.full_refresh, config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_read_with_board_ids_filter(self, http_mocker):
        """
        A full refresh sync of the boards stream with board filtering and without pagination
        """
        board_ids = [123, 456]
        config = ConfigBuilder().with_api_token_credentials("api-token").with_board_ids(board_ids).build()
        api_token_authenticator = self.get_authenticator(config)

        http_mocker.get(
            BoardsRequestBuilder.boards_endpoint(api_token_authenticator, board_ids).build(),
            BoardsResponseBuilder.boards_response().with_record(BoardsRecordBuilder.boards_record()).build(),
        )

        output = read_stream("boards", SyncMode.full_refresh, config)
        assert len(output.records) == 1
