#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from unittest import TestCase

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, create_response_builder, find_template
from airbyte_protocol.models import SyncMode

from .config import _ACCESS_TOKEN, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import build_response
from .utils import config, read_output

_STREAM_NAME = "VendorDirectFulfillmentShipping"


def _auth_request() -> RequestBuilder:
    """
    A POST request needed to refresh the access token.
    """

    return RequestBuilder.auth_endpoint()


def _request() -> RequestBuilder:
    return RequestBuilder.vendor_direct_fulfillment_shipping_endpoint()


def _auth_response() -> HttpResponse:
    response_body = {"access_token": _ACCESS_TOKEN, "expires_in": 3600, "token_type": "bearer"}
    return build_response(response_body, status_code=200)


def _response() -> HttpResponseBuilder:
    return create_response_builder(find_template(_STREAM_NAME, __file__), FieldPath("shippingLabels"))


class TestFullRefresh(TestCase):

    @staticmethod
    def _read(stream_name: str, config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(config, stream_name, SyncMode.full_refresh, expecting_exception=expecting_exception)

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        # mocking a POST request to auth endpoint
        http_mocker.post(_auth_request().build(), _auth_response())
        # mocking the actual stream request
        http_mocker.get(_request().build(), _response().build())
        output = self._read(_STREAM_NAME, config())
        assert len(output.records) == 0
