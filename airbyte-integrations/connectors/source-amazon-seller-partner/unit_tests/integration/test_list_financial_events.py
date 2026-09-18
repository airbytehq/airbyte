#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


from http import HTTPStatus

import freezegun
import pendulum

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker

from .config import NOW, TIME_FORMAT, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import build_response, response_with_status
from .utils import config, mock_auth, read_output


_START_DATE = pendulum.datetime(year=2023, month=1, day=1)
_END_DATE = pendulum.datetime(year=2023, month=1, day=30)
_STREAM_NAME = "ListFinancialEvents"

# Amazon answers a window whose page exceeds the transaction cap or 10 MB with HTTP 400 and this
# body. It is not a statement about the request being malformed, which is why the connector answers
# it by asking for a smaller page rather than by failing.
_INVALID_INPUT = {"errors": [{"code": "InvalidInput", "message": "Invalid Input", "details": ""}]}
_ONE_EVENT = {"payload": {"FinancialEvents": {"ShipmentEventList": [{"AmazonOrderId": "123-4567890-1234567"}]}}}


def _request(max_results_per_page: int) -> RequestBuilder:
    return RequestBuilder.list_financial_events_endpoint().with_query_params(
        {
            "PostedAfter": _START_DATE.strftime(TIME_FORMAT),
            "PostedBefore": _END_DATE.strftime(TIME_FORMAT),
            "MaxResultsPerPage": str(max_results_per_page),
        }
    )


@freezegun.freeze_time(NOW.isoformat())
class TestPageSizeReduction:
    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_given_invalid_input_when_read_then_retry_the_same_page_with_a_smaller_page_size(self, http_mocker: HttpMocker) -> None:
        """
        The window is read at 100 records per page, rejected, then re-read at 50 and at 25 without the user
        touching the configuration. Before `REDUCE_PAGE_SIZE` the first response ended the sync with an error
        telling them to lower 'Financial Events Max Results Per Page' by hand and start over.

        HttpMocker requires every registered request to be made, so the two rejected page sizes are asserted
        by being mocked at all.
        """
        mock_auth(http_mocker)
        http_mocker.get(_request(100).build(), response_with_status(HTTPStatus.BAD_REQUEST, _INVALID_INPUT))
        http_mocker.get(_request(50).build(), response_with_status(HTTPStatus.BAD_REQUEST, _INVALID_INPUT))
        http_mocker.get(_request(25).build(), build_response(_ONE_EVENT, HTTPStatus.OK))

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_no_invalid_input_when_read_then_the_configured_page_size_is_kept(self, http_mocker: HttpMocker) -> None:
        # The reduction is only reachable from a rejected page: nothing changes for a window the API accepts.
        mock_auth(http_mocker)
        http_mocker.get(_request(100).build(), build_response(_ONE_EVENT, HTTPStatus.OK))

        output = self._read(config().with_start_date(_START_DATE).with_end_date(_END_DATE))

        assert len(output.records) == 1
