#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import gzip
from datetime import datetime, timezone
from test.mock_http.matcher import HttpRequestMatcher
from typing import Optional

import freezegun
import pytest
import requests_mock
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_protocol.models import FailureType, SyncMode
from source_amazon_seller_partner.streams import ReportProcessingStatus

from .config import _ACCESS_TOKEN, _MARKETPLACE_ID, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import build_response
from .utils import config, find_template, read_output

_DOCUMENT_DOWNLOAD_URL = "https://test.com/download"
_NOW = datetime.now(timezone.utc)
_REPORT_ID = "6789087632"
_REPORT_DOCUMENT_ID = "report_document_id"

# every test file in resource/http/response contains 2 records
EXPECTED_NUMBER_OF_RECORDS = 2

STREAMS = {
    ("GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING", "csv"),
    ("GET_ORDER_REPORT_DATA_SHIPPING", "xml"),
    ("GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL", "csv"),
    ("GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA", "csv"),
    ("GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA", "csv"),
    ("GET_SELLER_FEEDBACK_DATA", "csv"),
    ("GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA", "csv"),
    ("GET_LEDGER_DETAIL_VIEW_DATA", "csv"),
    ("GET_AFN_INVENTORY_DATA_BY_COUNTRY", "csv"),
    ("GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE", "csv"),
    ("GET_VENDOR_SALES_REPORT", "json"),
    ("GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT", "json"),
    ("GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA", "csv"),
    ("GET_FBA_SNS_FORECAST_DATA", "csv"),
    ("GET_AFN_INVENTORY_DATA", "csv"),
    ("GET_MERCHANT_CANCELLED_LISTINGS_DATA", "csv"),
    ("GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA", "csv"),
    ("GET_LEDGER_SUMMARY_VIEW_DATA", "csv"),
    ("GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT", "json"),
    ("GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT", "json"),
    ("GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE", "csv"),
    ("GET_VENDOR_INVENTORY_REPORT", "json"),
    ("GET_FBA_SNS_PERFORMANCE_DATA", "csv"),
    ("GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA", "csv"),
    ("GET_FBA_INVENTORY_PLANNING_DATA", "csv"),
    ("GET_FBA_STORAGE_FEE_CHARGES_DATA", "csv"),
    # ("GET_SALES_AND_TRAFFIC_REPORT", "json"),
    ("GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA", "csv"),
    ("GET_STRANDED_INVENTORY_UI_DATA", "csv"),
    ("GET_FBA_REIMBURSEMENTS_DATA", "csv"),
    ("GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT", "json"),
    ("GET_VENDOR_REAL_TIME_INVENTORY_REPORT", "json"),
    ("GET_VENDOR_TRAFFIC_REPORT", "json"),
}


def _mock_auth(http_mocker: HttpMocker) -> None:
    response_body = {"access_token": _ACCESS_TOKEN, "expires_in": 3600, "token_type": "bearer"}
    http_mocker.post(RequestBuilder.auth_endpoint().build(), build_response(response_body, status_code=200))


def _create_report_request(report_name: str) -> RequestBuilder:
    """
    A POST request needed to start generating a report on Amazon SP platform.
    Performed in ReportsAmazonSPStream._create_report method.
    """

    return RequestBuilder.create_report_endpoint(report_name)


def _check_report_status_request(report_id: str) -> RequestBuilder:
    """
    A GET request needed to check the report generating status.
    Performed in ReportsAmazonSPStream._retrieve_report method.
    """

    return RequestBuilder.check_report_status_endpoint(report_id)


def _get_document_download_url_request(document_id: str) -> RequestBuilder:
    """
    A GET request which returns a URL for the report download.
    """

    return RequestBuilder.get_document_download_url_endpoint(document_id)


def _download_document_request(url: str) -> RequestBuilder:
    """
    A GET request which actually downloads the report.
    Performed in ReportsAmazonSPStream.download_and_decompress_report_document method.
    """

    return RequestBuilder.download_document_endpoint(url)


def _create_report_response(status_code: Optional[int] = 202) -> HttpResponse:
    response_body = {"reportId": _REPORT_ID}
    return build_response(response_body, status_code=status_code)


def _check_report_status_response(
    report_name: str, processing_status: Optional[ReportProcessingStatus] = ReportProcessingStatus.done
) -> HttpResponse:
    response_body = {
        "reportType": report_name,
        "processingStatus": processing_status,
        "marketplaceIds": [_MARKETPLACE_ID],
        "reportId": _REPORT_ID,
        # TODO: check what to do with these dates
        "dataEndTime": "2022-11-29T23:59:59+00:00",
        "createdTime": "2024-01-10T12:55:55+00:00",
        "dataStartTime": "2022-09-01T00:00:00+00:00",
    }
    if processing_status == ReportProcessingStatus.done:
        response_body.update(
            {
                "reportDocumentId": _REPORT_DOCUMENT_ID,
                "processingEndTime": "2024-01-10T13:30:43+00:00",
                "processingStartTime": "2024-01-10T13:30:31+00:00",
            }
        )

    return build_response(response_body, status_code=200)


def _get_document_download_url_response(compressed: Optional[bool] = False) -> HttpResponse:
    response_body = {"reportDocumentId": _REPORT_DOCUMENT_ID, "url": _DOCUMENT_DOWNLOAD_URL}
    if compressed:
        # See https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference#compressionalgorithm
        response_body["compressionAlgorithm"] = "GZIP"
    return build_response(response_body, status_code=200)


def _download_document_response(stream_name: str, data_format: Optional[str] = "csv", compressed: Optional[bool] = False) -> HttpResponse:
    response_body = find_template(stream_name, __file__, data_format)
    if compressed:
        response_body = gzip.compress(response_body.encode("iso-8859-1"))
    return HttpResponse(body=response_body, status_code=200)


@pytest.fixture(name="http_mocker")
def _http_mocker() -> None:
    """This fixture is needed to pass http_mocker parameter from the @HttpMocker decorator to a test"""
    ...


@freezegun.freeze_time(_NOW.isoformat())
class TestFullRefresh:

    @staticmethod
    def _read(stream_name: str, config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(config_, stream_name, SyncMode.full_refresh, expecting_exception=expecting_exception)

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_report_when_read_then_return_records(self, stream_name: str, data_format: str, http_mocker: HttpMocker) -> None:
        _mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response())
        http_mocker.get(_check_report_status_request(_REPORT_ID).build(), _check_report_status_response(stream_name))
        http_mocker.get(_get_document_download_url_request(_REPORT_DOCUMENT_ID).build(), _get_document_download_url_response())
        http_mocker.get(
            _download_document_request(_DOCUMENT_DOWNLOAD_URL).build(),
            _download_document_response(stream_name, data_format=data_format),
        )

        output = self._read(stream_name, config())
        assert len(output.records) == EXPECTED_NUMBER_OF_RECORDS

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_compressed_report_when_read_then_return_records(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        _mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response())
        http_mocker.get(_check_report_status_request(_REPORT_ID).build(), _check_report_status_response(stream_name))
        http_mocker.get(
            _get_document_download_url_request(_REPORT_DOCUMENT_ID).build(), _get_document_download_url_response(compressed=True)
        )

        # a workaround to pass compressed document to the mocked response
        document_request = _download_document_request(_DOCUMENT_DOWNLOAD_URL).build()
        document_response = _download_document_response(stream_name, data_format=data_format, compressed=True)
        document_request_matcher = HttpRequestMatcher(document_request, minimum_number_of_expected_match=1)
        http_mocker._matchers.append(document_request_matcher)

        http_mocker._mocker.get(
            requests_mock.ANY,
            additional_matcher=http_mocker._matches_wrapper(document_request_matcher),
            response_list=[{"content": document_response.body, "status_code": document_response.status_code}],
        )

        output = self._read(stream_name, config())
        assert len(output.records) == EXPECTED_NUMBER_OF_RECORDS

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_report_access_forbidden_when_read_then_no_records(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        _mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(status_code=403))

        output = self._read(stream_name, config())
        assert len(output.records) == 0

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_report_status_cancelled_when_read_then_no_records(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        _mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response())
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, processing_status=ReportProcessingStatus.cancelled),
        )

        output = self._read(stream_name, config())
        assert len(output.records) == 0

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_report_status_fatal_when_read_then_exception_raised(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        _mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response())
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, processing_status=ReportProcessingStatus.fatal),
        )

        output = self._read(stream_name, config(), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.system_error
        assert output.errors[-1].trace.error.message == f"The report for stream '{stream_name}' was not created - skip reading"

    @pytest.mark.parametrize(
        ("stream_name", "date_field", "expected_date_value"),
        (
            ("GET_SELLER_FEEDBACK_DATA", "date", "2020-10-20"),
            ("GET_LEDGER_DETAIL_VIEW_DATA", "Date", "2021-11-21"),
            ("GET_LEDGER_SUMMARY_VIEW_DATA", "Date", "2022-12-22"),
        ),
    )
    @HttpMocker()
    def test_given_report_with_incorrect_date_format_when_read_then_formatted(
        self, stream_name: str, date_field: str, expected_date_value: str, http_mocker: HttpMocker
    ) -> None:
        _mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response())
        http_mocker.get(_check_report_status_request(_REPORT_ID).build(), _check_report_status_response(stream_name))
        http_mocker.get(_get_document_download_url_request(_REPORT_DOCUMENT_ID).build(), _get_document_download_url_response())
        http_mocker.get(_download_document_request(_DOCUMENT_DOWNLOAD_URL).build(), _download_document_response(stream_name))

        output = self._read(stream_name, config())
        assert len(output.records) == 2
        assert output.records[0].record.data.get(date_field) == expected_date_value
