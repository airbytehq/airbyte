#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import gzip
from http import HTTPStatus
from typing import List, Optional

import freezegun
import pytest
import requests_mock
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.matcher import HttpRequestMatcher
from airbyte_protocol.models import AirbyteStateMessage, FailureType, SyncMode
from source_amazon_seller_partner.streams import ReportProcessingStatus

from .config import CONFIG_END_DATE, CONFIG_START_DATE, MARKETPLACE_ID, NOW, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import build_response, response_with_status
from .utils import assert_message_in_log_output, config, find_template, get_stream_by_name, mock_auth, read_output

_DOCUMENT_DOWNLOAD_URL = "https://test.com/download"
_REPORT_ID = "6789087632"
_REPORT_DOCUMENT_ID = "report_document_id"

DEFAULT_EXPECTED_NUMBER_OF_RECORDS = 2  # every test file in resource/http/response contains 2 records
STREAMS = (
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
    ("GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA", "csv"),
    ("GET_STRANDED_INVENTORY_UI_DATA", "csv"),
    ("GET_FBA_REIMBURSEMENTS_DATA", "csv"),
    ("GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT", "json"),
    ("GET_VENDOR_REAL_TIME_INVENTORY_REPORT", "json"),
    ("GET_VENDOR_TRAFFIC_REPORT", "json"),
)


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


def _create_report_response(report_id: str, status_code: Optional[HTTPStatus] = HTTPStatus.ACCEPTED) -> HttpResponse:
    response_body = {"reportId": report_id}
    return build_response(response_body, status_code=status_code)


def _check_report_status_response(
    report_name: str,
    processing_status: Optional[ReportProcessingStatus] = ReportProcessingStatus.DONE,
    report_document_id: Optional[str] = None,
) -> HttpResponse:
    if processing_status == ReportProcessingStatus.DONE and not report_document_id:
        raise ValueError("report_document_id value should be passed when processing_status is 'DONE'.")

    response_body = {
        "reportType": report_name,
        "processingStatus": processing_status,
        "marketplaceIds": [MARKETPLACE_ID],
        "reportId": _REPORT_ID,
        "dataEndTime": CONFIG_END_DATE,
        "createdTime": CONFIG_START_DATE,
        "dataStartTime": CONFIG_START_DATE,
    }
    if processing_status == ReportProcessingStatus.DONE:
        response_body.update(
            {
                "reportDocumentId": report_document_id,
                "processingEndTime": CONFIG_START_DATE,
                "processingStartTime": CONFIG_START_DATE,
            }
        )

    return build_response(response_body, status_code=HTTPStatus.OK)


def _get_document_download_url_response(
    document_download_url: str, report_document_id: str, compressed: Optional[bool] = False
) -> HttpResponse:
    response_body = {"reportDocumentId": report_document_id, "url": document_download_url}
    if compressed:
        # See https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference#compressionalgorithm
        response_body["compressionAlgorithm"] = "GZIP"
    return build_response(response_body, status_code=HTTPStatus.OK)


def _download_document_response(
    stream_name: str, data_format: Optional[str] = "csv", compressed: Optional[bool] = False
) -> HttpResponse:
    response_body = find_template(stream_name, __file__, data_format)
    if compressed:
        response_body = gzip.compress(response_body.encode("iso-8859-1"))
    return HttpResponse(body=response_body, status_code=HTTPStatus.OK)


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh:

    @staticmethod
    def _read(stream_name: str, config_: ConfigBuilder, expecting_exception: bool = False) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=stream_name,
            sync_mode=SyncMode.full_refresh,
            expecting_exception=expecting_exception,
        )

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_report_when_read_then_return_records(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(_REPORT_ID))
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, report_document_id=_REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _get_document_download_url_request(_REPORT_DOCUMENT_ID).build(),
            _get_document_download_url_response(_DOCUMENT_DOWNLOAD_URL, _REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _download_document_request(_DOCUMENT_DOWNLOAD_URL).build(),
            _download_document_response(stream_name, data_format=data_format),
        )

        output = self._read(stream_name, config())
        assert len(output.records) == DEFAULT_EXPECTED_NUMBER_OF_RECORDS

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_compressed_report_when_read_then_return_records(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(_REPORT_ID))
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, report_document_id=_REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _get_document_download_url_request(_REPORT_DOCUMENT_ID).build(),
            _get_document_download_url_response(_DOCUMENT_DOWNLOAD_URL, _REPORT_DOCUMENT_ID, compressed=True),
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
        assert len(output.records) == DEFAULT_EXPECTED_NUMBER_OF_RECORDS

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_http_status_500_then_200_when_create_report_then_retry_and_return_records(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)
        http_mocker.post(
            _create_report_request(stream_name).build(),
            [response_with_status(status_code=HTTPStatus.INTERNAL_SERVER_ERROR), _create_report_response(_REPORT_ID)],
        )
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, report_document_id=_REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _get_document_download_url_request(_REPORT_DOCUMENT_ID).build(),
            _get_document_download_url_response(_DOCUMENT_DOWNLOAD_URL, _REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _download_document_request(_DOCUMENT_DOWNLOAD_URL).build(),
            _download_document_response(stream_name, data_format=data_format),
        )

        output = self._read(stream_name, config())
        assert len(output.records) == DEFAULT_EXPECTED_NUMBER_OF_RECORDS

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_http_status_500_then_200_when_retrieve_report_then_retry_and_return_records(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)
        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(_REPORT_ID))
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            [
                response_with_status(status_code=HTTPStatus.INTERNAL_SERVER_ERROR),
                _check_report_status_response(stream_name, report_document_id=_REPORT_DOCUMENT_ID),
            ],
        )
        http_mocker.get(
            _get_document_download_url_request(_REPORT_DOCUMENT_ID).build(),
            _get_document_download_url_response(_DOCUMENT_DOWNLOAD_URL, _REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _download_document_request(_DOCUMENT_DOWNLOAD_URL).build(),
            _download_document_response(stream_name, data_format=data_format),
        )

        output = self._read(stream_name, config())
        assert len(output.records) == DEFAULT_EXPECTED_NUMBER_OF_RECORDS

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_http_status_500_then_200_when_get_document_url_then_retry_and_return_records(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)
        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(_REPORT_ID))
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, report_document_id=_REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _get_document_download_url_request(_REPORT_DOCUMENT_ID).build(),
            [
                response_with_status(status_code=HTTPStatus.INTERNAL_SERVER_ERROR),
                _get_document_download_url_response(_DOCUMENT_DOWNLOAD_URL, _REPORT_DOCUMENT_ID),
            ],
        )
        http_mocker.get(
            _download_document_request(_DOCUMENT_DOWNLOAD_URL).build(),
            _download_document_response(stream_name, data_format=data_format),
        )

        output = self._read(stream_name, config())
        assert len(output.records) == DEFAULT_EXPECTED_NUMBER_OF_RECORDS

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_http_status_500_then_200_when_download_document_then_retry_and_return_records(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)
        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(_REPORT_ID))
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, report_document_id=_REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _get_document_download_url_request(_REPORT_DOCUMENT_ID).build(),
            _get_document_download_url_response(_DOCUMENT_DOWNLOAD_URL, _REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _download_document_request(_DOCUMENT_DOWNLOAD_URL).build(),
            [
                response_with_status(status_code=HTTPStatus.INTERNAL_SERVER_ERROR),
                _download_document_response(stream_name, data_format=data_format),
            ],
        )

        output = self._read(stream_name, config())
        assert len(output.records) == DEFAULT_EXPECTED_NUMBER_OF_RECORDS

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_report_access_forbidden_when_read_then_no_records_and_error_logged(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)

        http_mocker.post(
            _create_report_request(stream_name).build(), response_with_status(status_code=HTTPStatus.FORBIDDEN)
        )

        output = self._read(stream_name, config())
        message_on_access_forbidden = (
            "This is most likely due to insufficient permissions on the credentials in use. "
            "Try to grant required permissions/scopes or re-authenticate."
        )
        assert_message_in_log_output(message_on_access_forbidden, output)
        assert len(output.records) == 0

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_report_status_cancelled_when_read_then_stream_completed_successfully_and_warn_about_cancellation(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(_REPORT_ID))
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, processing_status=ReportProcessingStatus.CANCELLED),
        )

        message_on_report_cancelled = (
            f"The report for stream '{stream_name}' was cancelled or there is no data to return."
        )

        output = self._read(stream_name, config())
        assert_message_in_log_output(message_on_report_cancelled, output)
        assert len(output.records) == 0

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_report_status_fatal_when_read_then_exception_raised(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(_REPORT_ID))
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, processing_status=ReportProcessingStatus.FATAL),
        )

        output = self._read(stream_name, config(), expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.system_error
        assert output.errors[-1].trace.error.internal_message == (
            f"Failed to retrieve the report '{stream_name}' for period {CONFIG_START_DATE}-{CONFIG_END_DATE} "
            "due to Amazon Seller Partner platform issues. This will be read during the next sync."
        )

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
        mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(_REPORT_ID))
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, report_document_id=_REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _get_document_download_url_request(_REPORT_DOCUMENT_ID).build(),
            _get_document_download_url_response(_DOCUMENT_DOWNLOAD_URL, _REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _download_document_request(_DOCUMENT_DOWNLOAD_URL).build(), _download_document_response(stream_name)
        )

        output = self._read(stream_name, config())
        assert len(output.records) == DEFAULT_EXPECTED_NUMBER_OF_RECORDS
        assert output.records[0].record.data.get(date_field) == expected_date_value

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_http_error_500_on_create_report_when_read_then_no_records_and_error_logged(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)

        http_mocker.post(
            _create_report_request(stream_name).build(),
            response_with_status(status_code=HTTPStatus.INTERNAL_SERVER_ERROR),
        )

        message_on_backoff_exception = (
            f"The report for stream '{stream_name}' was cancelled due to several failed retry attempts."
        )

        output = self._read(stream_name, config())
        assert_message_in_log_output(message_on_backoff_exception, output)
        assert len(output.records) == 0


@freezegun.freeze_time(NOW.isoformat())
class TestIncremental:
    default_cursor_field = "dataEndTime"

    @staticmethod
    def _read(
        stream_name: str,
        config_: ConfigBuilder,
        state: Optional[List[AirbyteStateMessage]] = None,
        expecting_exception: bool = False,
    ) -> EntrypointOutput:
        return read_output(
            config_builder=config_,
            stream_name=stream_name,
            sync_mode=SyncMode.incremental,
            state=state,
            expecting_exception=expecting_exception,
        )

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_report_when_read_then_default_cursor_field_added_to_every_record(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(_REPORT_ID))
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, report_document_id=_REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _get_document_download_url_request(_REPORT_DOCUMENT_ID).build(),
            _get_document_download_url_response(_DOCUMENT_DOWNLOAD_URL, _REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _download_document_request(_DOCUMENT_DOWNLOAD_URL).build(),
            _download_document_response(stream_name, data_format=data_format),
        )

        output = self._read(stream_name, config())
        assert all([self.default_cursor_field in record.record.data for record in output.records])

    @pytest.mark.parametrize(("stream_name", "data_format"), STREAMS)
    @HttpMocker()
    def test_given_report_when_read_then_state_message_produced_and_state_match_latest_record(
        self, stream_name: str, data_format: str, http_mocker: HttpMocker
    ) -> None:
        _config = config()
        mock_auth(http_mocker)

        http_mocker.post(_create_report_request(stream_name).build(), _create_report_response(_REPORT_ID))
        http_mocker.get(
            _check_report_status_request(_REPORT_ID).build(),
            _check_report_status_response(stream_name, report_document_id=_REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _get_document_download_url_request(_REPORT_DOCUMENT_ID).build(),
            _get_document_download_url_response(_DOCUMENT_DOWNLOAD_URL, _REPORT_DOCUMENT_ID),
        )
        http_mocker.get(
            _download_document_request(_DOCUMENT_DOWNLOAD_URL).build(),
            _download_document_response(stream_name, data_format=data_format),
        )

        output = self._read(stream_name, _config)
        assert len(output.state_messages) == 1

        cursor_field = get_stream_by_name(stream_name, _config.build()).cursor_field
        cursor_value_from_state_message = output.most_recent_state.get(stream_name, {}).get(cursor_field)
        cursor_value_from_latest_record = output.records[-1].record.data.get(cursor_field)
        assert cursor_value_from_state_message == cursor_value_from_latest_record
