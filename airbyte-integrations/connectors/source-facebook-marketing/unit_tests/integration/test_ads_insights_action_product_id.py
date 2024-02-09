#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Optional
from unittest import TestCase

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.matcher import HttpRequestMatcher
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponse,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_protocol.models import SyncMode
import requests_mock

from .config import ACCESS_TOKEN, ACCOUNT_ID, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import build_response
from .utils import config, read_output

_STREAM_NAME = "ads_insights_action_product_id"
_CURSOR_FIELD = "date_start"


def _get_account_request() -> RequestBuilder:
    return RequestBuilder.get_account_endpoint(account_id=ACCOUNT_ID, access_token=ACCESS_TOKEN)


def _update_api_throttle_limit_request() -> RequestBuilder:
    return RequestBuilder.get_insights_endpoint(account_id=ACCOUNT_ID, access_token=ACCESS_TOKEN)


def _get_account_response(account_id: Optional[str] = ACCOUNT_ID) -> HttpResponse:
    response = {"account_id": account_id, "id": f"act_{account_id}"}
    return build_response(body=response, status_code=HTTPStatus.OK)


def _update_api_throttle_limit_response() -> HttpResponse:
    body = {}
    # headers = {"x-fb-ads-insights-throttle": {"app_id_util_pct": 0.21, "acc_id_util_pct": 0, "ads_api_access_tier": "standard_access"}}
    headers = {"x-fb-ads-insights-throttle": '{"app_id_util_pct":0.21,"acc_id_util_pct":0,"ads_api_access_tier":"standard_access"}'}
    response = build_response(body=body, status_code=HTTPStatus.OK)
    # setattr(response, "headers", json.dumps(headers))
    setattr(response, "headers", headers)
    return response


def _ads_insights_action_product_id_record() -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath("data"),
        record_cursor_path=FieldPath(_CURSOR_FIELD),
    )


class TestFullRefresh(TestCase):

    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_, stream_name=_STREAM_NAME, sync_mode=SyncMode.full_refresh, expecting_exception=expecting_exception
        )

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        # api.get_account
        http_mocker.get(_get_account_request().build(), _get_account_response())

        # ----------------------------------------------
        throttle_limit_request = _update_api_throttle_limit_request().build()
        throttle_limit_response = _update_api_throttle_limit_response()
        http_mocker.get(throttle_limit_request, throttle_limit_response)

        throttle_limit_request_matcher = HttpRequestMatcher(throttle_limit_request, minimum_number_of_expected_match=1)
        http_mocker._matchers.append(throttle_limit_request_matcher)

        http_mocker._mocker.get(
            requests_mock.ANY,
            additional_matcher=http_mocker._matches_wrapper(throttle_limit_request_matcher),
            response_list=[
                {
                    "text": throttle_limit_response.body,
                    "status_code": throttle_limit_response.status_code,
                    "headers": throttle_limit_response.headers,
                },
            ],
        )
        # ----------------------------------------------

        output = self._read(config())
        assert len(output.records) == 0
