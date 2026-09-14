#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""
Mock-server tests for `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE`.

Settlement reports are generated automatically by Amazon and cannot be requested, so the stream
lists existing reports (`getReports`), resolves each `reportDocumentId` to a pre-signed URL
(`getReportDocument`) and downloads that URL without SP-API authentication.
"""

import gzip
from http import HTTPStatus

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .config import MARKETPLACE_ID, NOW, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import build_response
from .utils import config, find_template, mock_auth, read_output


_STREAM_NAME = "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE"
_RECORDS_PER_DOCUMENT = 2  # the fixture in resource/http/response contains 2 data rows

_DONE_REPORT_ID = "1111111111"
_DONE_REPORT_DOCUMENT_ID = "amzn1.spdoc.1.done"
_DONE_DOWNLOAD_URL = "https://tortuga-prod-na.s3.amazonaws.com/done-report"

_SECOND_DONE_REPORT_ID = "2222222222"
_SECOND_DONE_REPORT_DOCUMENT_ID = "amzn1.spdoc.1.second"
_SECOND_DONE_DOWNLOAD_URL = "https://tortuga-prod-na.s3.amazonaws.com/second-report"

_IN_PROGRESS_REPORT_ID = "3333333333"

# Amazon rejects `createdSince` older than 90 days, so the manifest clamps the window to the last 89 days.
# Keep the configured window inside that range so the helper stream produces a slice.
_START_DATE = NOW.subtract(days=30)
_END_DATE = NOW


def _config() -> ConfigBuilder:
    return config().with_start_date(_START_DATE).with_end_date(_END_DATE)


def _report(report_id: str, processing_status: str, report_document_id: str | None = None) -> dict:
    report = {
        "reportType": _STREAM_NAME,
        "processingStatus": processing_status,
        "marketplaceIds": [MARKETPLACE_ID],
        "reportId": report_id,
        "dataStartTime": NOW.subtract(days=20).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dataEndTime": NOW.subtract(days=6).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "createdTime": NOW.subtract(days=5).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if report_document_id:
        report["reportDocumentId"] = report_document_id
    return report


def _list_reports_request() -> HttpRequest:
    return (
        RequestBuilder.get_reports_endpoint()
        .with_query_params(
            {
                "reportTypes": _STREAM_NAME,
                "pageSize": "100",
                "createdSince": _START_DATE.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "createdUntil": _END_DATE.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        )
        .build()
    )


def _list_reports_response(reports: list[dict]) -> HttpResponse:
    return build_response({"reports": reports}, status_code=HTTPStatus.OK)


def _document_response(report_document_id: str, url: str, compressed: bool = False) -> HttpResponse:
    body = {"reportDocumentId": report_document_id, "url": url}
    if compressed:
        body["compressionAlgorithm"] = "GZIP"
    return build_response(body, status_code=HTTPStatus.OK)


def _download_response(compressed: bool = False) -> HttpResponse:
    body = find_template(_STREAM_NAME, __file__, "csv")
    if compressed:
        body = gzip.compress(body.encode("iso-8859-1"))
    return HttpResponse(body=body, status_code=HTTPStatus.OK)


def _mock_document_chain(
    http_mocker: HttpMocker, report_document_id: str, url: str, compressed: bool = False
) -> tuple[HttpRequest, HttpRequest]:
    """Mocks `getReportDocument` and the pre-signed URL download; returns both requests for call-count assertions."""
    document_request = RequestBuilder.get_document_download_url_endpoint(report_document_id).build()
    download_request = RequestBuilder.download_document_endpoint(url).build()
    http_mocker.get(document_request, _document_response(report_document_id, url, compressed=compressed))
    http_mocker.get(download_request, _download_response(compressed=compressed))
    return document_request, download_request


@freezegun.freeze_time(NOW.isoformat())
@pytest.mark.parametrize(
    "compressed",
    [
        pytest.param(False, id="plain_tsv_document"),
        pytest.param(True, id="gzip_compressed_document"),
    ],
)
@HttpMocker()
def test_given_done_settlement_reports_when_read_then_documents_downloaded_and_records_emitted(
    compressed: bool, http_mocker: HttpMocker
) -> None:
    """
    Each `DONE` report listed by `getReports` must be resolved through `getReportDocument` and its
    pre-signed URL downloaded; reports that are not `DONE` carry no `reportDocumentId` and are skipped.
    """
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(
        _list_reports_request(),
        _list_reports_response(
            [
                _report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID),
                _report(_IN_PROGRESS_REPORT_ID, "IN_PROGRESS"),
                _report(_SECOND_DONE_REPORT_ID, "DONE", _SECOND_DONE_REPORT_DOCUMENT_ID),
            ]
        ),
    )
    first_chain = _mock_document_chain(http_mocker, _DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL, compressed=compressed)
    second_chain = _mock_document_chain(http_mocker, _SECOND_DONE_REPORT_DOCUMENT_ID, _SECOND_DONE_DOWNLOAD_URL, compressed=compressed)

    output = read_output(config_builder=_config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

    assert len(output.errors) == 0
    assert len(output.records) == 2 * _RECORDS_PER_DOCUMENT
    assert {record.record.data["settlement-id"] for record in output.records} == {"12345678901"}
    assert all("dataEndTime" in record.record.data for record in output.records)

    for request in (*first_chain, *second_chain):
        http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_document_lookup_forbidden_once_when_read_then_retried_and_records_emitted(http_mocker: HttpMocker) -> None:
    """A transient 403 from `getReportDocument` (e.g. expired token) must be retried instead of failing the stream."""
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(_list_reports_request(), _list_reports_response([_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID)]))
    document_request = RequestBuilder.get_document_download_url_endpoint(_DONE_REPORT_DOCUMENT_ID).build()
    http_mocker.get(
        document_request,
        [
            HttpResponse(body="", status_code=HTTPStatus.FORBIDDEN, headers={"x-amzn-RateLimit-Limit": "1000"}),
            _document_response(_DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL),
        ],
    )
    http_mocker.get(RequestBuilder.download_document_endpoint(_DONE_DOWNLOAD_URL).build(), _download_response())

    output = read_output(config_builder=_config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

    assert len(output.errors) == 0
    assert len(output.records) == _RECORDS_PER_DOCUMENT
    http_mocker.assert_number_of_calls(document_request, 2)


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_only_non_done_settlement_reports_when_read_then_no_document_requests_and_no_records(http_mocker: HttpMocker) -> None:
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(_list_reports_request(), _list_reports_response([_report(_IN_PROGRESS_REPORT_ID, "IN_PROGRESS")]))

    output = read_output(config_builder=_config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

    assert len(output.records) == 0
    assert len(output.errors) == 0
