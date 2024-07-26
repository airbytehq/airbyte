# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import SyncMode
from freezegun import freeze_time

from .config import ConfigBuilder
from .request_builder import get_product_attributes_request, get_product_attribute_terms_request
from .utils import config, get_json_http_response, read_output

_STREAM_NAME = "product_attribute_terms"


class TestFullRefresh(TestCase):

    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(config_, _STREAM_NAME, SyncMode.full_refresh)

    @HttpMocker()
    @freeze_time("2017-01-29T00:00:00Z")
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        # Register mock response
        http_mocker.get(
            get_product_attributes_request()
            .with_param("orderby", "id")
            .with_param("order", "asc")
            .with_param("dates_are_gmt", "true")
            .with_param("per_page", "100")
            .build(),
            get_json_http_response("product_attributes.json", 200),
            )

        for order_id in ["1", "2"]:
            http_mocker.get(
                get_product_attribute_terms_request(order_id)
                .with_param("orderby", "id")
                .with_param("order", "asc")
                .with_param("dates_are_gmt", "true")
                .with_param("per_page", "100")
                .build(),
                get_json_http_response("product_attribute_terms.json", 200),
                )

        # Read records
        output = self._read(config())

        # Check record count: 2 attributes, 7 terms per attribute.
        assert len(output.records) == 14
