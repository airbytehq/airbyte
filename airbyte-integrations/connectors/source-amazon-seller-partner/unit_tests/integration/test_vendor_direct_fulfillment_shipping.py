#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Optional
from unittest import TestCase

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, create_response_builder, find_template
from airbyte_protocol.models import ConfiguredAirbyteCatalog, SyncMode

from .config import ConfigBuilder
from .request_builder import RequestBuilder

from source_amazon_seller_partner import SourceAmazonSellerPartner

_STREAM_NAME = "VendorDirectFulfillmentShipping"


def _config() -> ConfigBuilder:
    return ConfigBuilder()


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _source() -> SourceAmazonSellerPartner:
    return SourceAmazonSellerPartner()


def _request() -> RequestBuilder:
    return RequestBuilder.vendor_direct_fulfillment_shipping_endpoint()


def _response() -> HttpResponseBuilder:
    return create_response_builder(find_template(_STREAM_NAME, __file__), FieldPath("shippingLabels"))


def _read(
    config_builder: ConfigBuilder, sync_mode: SyncMode, state: Optional[Dict[str, Any]] = None, expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    return read(_source(), config, catalog, state, expecting_exception)


class FullRefreshTest(TestCase):
    @staticmethod
    def _read(config: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, SyncMode.full_refresh, expecting_exception=expecting_exception)

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), _response().build())
        output = self._read(_config())
        assert len(output.records) == 2
