from unittest import TestCase
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import SyncMode
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from .config import ConfigBuilder
from .request_builder import RequestBuilder, get_customers_request
from .response_builder import get_customers_response
from .utils import read_output, config

_CURSOR_FIELD = "id"
_STREAM_NAME = "customers"


def _get_request() -> RequestBuilder:
    return (
        RequestBuilder.get_customers_endpoint().with_limit(100)
    )


def _get_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath('data'),
    )


def _record() -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(_STREAM_NAME, __file__),
        records_path=FieldPath('data'),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath(_CURSOR_FIELD),
    )


class TestFullRefresh(TestCase):

    @staticmethod
    def _read(config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=_STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            get_customers_request()
            .with_custom_param("orderby", "id")
            .with_custom_param("order", "asc")
            .with_custom_param("dates_are_gmt", "true")
            .with_custom_param("per_page", "100")
            .build(),
            get_customers_response(f"/Users/ecorona/PycharmProjects/airbyte/airbyte-integrations/connectors/source-woocommerce/unit_tests/resource/http/response/customers.json",
                                   200),
        )

        output = self._read(config_=config())

        assert len(output.records) == 2
