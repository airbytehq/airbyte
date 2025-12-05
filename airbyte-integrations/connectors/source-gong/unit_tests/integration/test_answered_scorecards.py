#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ANSWERED_SCORECARD_ID, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import (
    answered_scorecards_response,
    empty_response,
    error_response,
)
from .utils import config, read_output


_STREAM_NAME = "answeredScorecards"


def _read(
    config_builder: ConfigBuilder,
    sync_mode: SyncMode = SyncMode.full_refresh,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    return read_output(
        config_builder=config_builder,
        stream_name=_STREAM_NAME,
        sync_mode=sync_mode,
        expecting_exception=expecting_exception,
    )


class TestAnsweredScorecards(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            RequestBuilder.answered_scorecards_endpoint().with_any_query_params().build(),
            answered_scorecards_response(answered_scorecard_id=ANSWERED_SCORECARD_ID),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["answeredScorecardId"] == ANSWERED_SCORECARD_ID

    @HttpMocker()
    def test_read_records_empty(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            RequestBuilder.answered_scorecards_endpoint().with_any_query_params().build(),
            empty_response(stream_key="answeredScorecards"),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_records_with_pagination(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            RequestBuilder.answered_scorecards_endpoint().with_any_query_params().build(),
            [
                answered_scorecards_response(answered_scorecard_id="answered_1", has_next=True, cursor="cursor_1"),
                answered_scorecards_response(answered_scorecard_id="answered_2", has_next=False),
            ],
        )

        output = _read(config_builder=config())
        assert len(output.records) == 2

    @HttpMocker()
    def test_read_records_with_error_401(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            RequestBuilder.answered_scorecards_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.UNAUTHORIZED),
        )

        output = _read(config_builder=config(), expecting_exception=True)
        assert len(output.records) == 0
