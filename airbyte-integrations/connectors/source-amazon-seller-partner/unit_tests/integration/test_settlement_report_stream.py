#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""
Mock-server tests for `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE`.

Settlement reports are generated automatically by Amazon and cannot be requested, so the stream
lists existing reports (`getReports`), reads each one (`getReport`), resolves its `reportDocumentId`
to a pre-signed URL (`getReportDocument`) and downloads that URL without SP-API authentication.
"""

import gzip
from http import HTTPStatus

import freezegun
import pendulum
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.async_job.job_orchestrator import AsyncJobOrchestrator
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder

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

_THIRD_DONE_REPORT_ID = "4444444444"
_THIRD_DONE_REPORT_DOCUMENT_ID = "amzn1.spdoc.1.third"
_THIRD_DONE_DOWNLOAD_URL = "https://tortuga-prod-na.s3.amazonaws.com/third-report"

_IN_PROGRESS_REPORT_ID = "3333333333"
_IN_PROGRESS_REPORT_DOCUMENT_ID = "amzn1.spdoc.1.in-progress"
_IN_PROGRESS_DOWNLOAD_URL = "https://tortuga-prod-na.s3.amazonaws.com/in-progress-report"

_CANCELLED_REPORT_ID = "5555555555"
_FATAL_REPORT_ID = "6666666666"

_NEXT_TOKEN = "next-page-token"
_NEXT_TOKEN_2 = "next-page-token-2"

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


def _list_reports_request(created_since: pendulum.DateTime = _START_DATE, created_until: pendulum.DateTime = _END_DATE) -> HttpRequest:
    """
    The first `getReports` request of a slice, carrying the full filter set. Ignores `x-amz-date` so tests can sync at
    times other than `NOW`.
    """
    return (
        RequestBuilder.get_reports_endpoint()
        .without_amz_date()
        .with_query_params(
            {
                "reportTypes": _STREAM_NAME,
                "pageSize": "100",
                "createdSince": created_since.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "createdUntil": created_until.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        )
        .build()
    )


def _list_reports_next_page_request(next_token: str) -> HttpRequest:
    """
    A paginated `getReports` request. Amazon's reports_2021-06-30 model: "include this token as the
    only parameter. Specifying `nextToken` with any other parameters will cause the request to fail."
    `HttpRequest.matches` compares query params for equality, so this asserts that no other parameter
    is sent alongside the token.
    """
    return RequestBuilder.get_reports_endpoint().with_query_params({"nextToken": next_token}).build()


def _state_with_listing_checkpoint(checkpoint: pendulum.DateTime) -> list:
    """State as persisted by the stream, with the report-listing helper's cursor set to `checkpoint`."""
    cursor = checkpoint.strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        StateBuilder()
        .with_stream_state(
            _STREAM_NAME,
            {
                "use_global_cursor": False,
                "states": [],
                "state": {"dataEndTime": cursor},
                "lookback_window": 0,
                "parent_state": {"flat_file_settlement_v2_helper": {"listedUntil": cursor}},
            },
        )
        .build()
    )


def _state_written_by_6_1_0(listing_start: pendulum.DateTime, sync_at: pendulum.DateTime, listed_report_ids: list[str]) -> list:
    """
    State as persisted by 6.1.0, which listed reports without downloading them (captured from a 6.1.0 sync): the
    listing checkpoint is stored under `dataEndTime`, truncated to midnight of the sync's UTC day, and each listed
    report has a partition whose cursor never moved past the listing start because it emitted no records.
    """
    return (
        StateBuilder()
        .with_stream_state(
            _STREAM_NAME,
            {
                "use_global_cursor": False,
                "states": [
                    {
                        "partition": {"parent_slice": {}, "reportId": report_id},
                        "cursor": {"dataEndTime": listing_start.strftime("%Y-%m-%dT%H:%M:%SZ")},
                    }
                    for report_id in listed_report_ids
                ],
                "lookback_window": 0,
                "parent_state": {"flat_file_settlement_v2_helper": {"dataEndTime": sync_at.start_of("day").strftime("%Y-%m-%dT%H:%M:%SZ")}},
            },
        )
        .build()
    )


def _listing_checkpoint(output: EntrypointOutput) -> str:
    """The `getReports` listing checkpoint in the last state message, which is where the next sync starts listing."""
    return output.most_recent_state.stream_state.__dict__["parent_state"]["flat_file_settlement_v2_helper"]["listedUntil"]


def _list_reports_response(reports: list[dict], next_token: str | None = None) -> HttpResponse:
    body = {"reports": reports}
    if next_token:
        body["nextToken"] = next_token
    return build_response(body, status_code=HTTPStatus.OK)


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


def _expired_url_response() -> HttpResponse:
    return HttpResponse(
        body="<Error><Code>AccessDenied</Code><Message>Request has expired</Message></Error>",
        status_code=HTTPStatus.FORBIDDEN,
    )


def _mock_report_chain(
    http_mocker: HttpMocker,
    report_id: str,
    report_document_id: str,
    url: str,
    compressed: bool = False,
) -> tuple[HttpRequest, HttpRequest, HttpRequest]:
    """
    Mocks the per-report chain: `getReport` (used for both the job creation and polling requests),
    `getReportDocument`, and the pre-signed URL download. Returns the three requests for call-count
    assertions. Ignores `x-amz-date` so tests can sync at times other than `NOW`.
    """
    report_request = RequestBuilder.check_report_status_endpoint(report_id).without_amz_date().build()
    document_request = RequestBuilder.get_document_download_url_endpoint(report_document_id).without_amz_date().build()
    download_request = RequestBuilder.download_document_endpoint(url).build()
    http_mocker.get(report_request, build_response(_report(report_id, "DONE", report_document_id), status_code=HTTPStatus.OK))
    http_mocker.get(document_request, _document_response(report_document_id, url, compressed=compressed))
    http_mocker.get(download_request, _download_response(compressed=compressed))
    return report_request, document_request, download_request


def _requested_urls(http_mocker: HttpMocker) -> list[str]:
    """
    Ordered list of every URL the connector requested. Reaches into the underlying `requests_mock`
    because `HttpMocker` only exposes call counts, and the ordering is the property under test for
    the pre-signed URL: it must be minted immediately before it is used.
    """
    return [request.url for request in http_mocker._mocker.request_history]


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
    pre-signed URL downloaded; `CANCELLED` and `FATAL` reports have no document and are skipped.
    """
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(
        _list_reports_request(),
        _list_reports_response(
            [
                _report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID),
                _report(_CANCELLED_REPORT_ID, "CANCELLED"),
                _report(_SECOND_DONE_REPORT_ID, "DONE", _SECOND_DONE_REPORT_DOCUMENT_ID),
                _report(_FATAL_REPORT_ID, "FATAL"),
            ]
        ),
    )
    _, first_document, first_download = _mock_report_chain(
        http_mocker, _DONE_REPORT_ID, _DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL, compressed=compressed
    )
    _, second_document, second_download = _mock_report_chain(
        http_mocker, _SECOND_DONE_REPORT_ID, _SECOND_DONE_REPORT_DOCUMENT_ID, _SECOND_DONE_DOWNLOAD_URL, compressed=compressed
    )

    output = read_output(config_builder=_config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

    assert len(output.errors) == 0
    assert len(output.records) == 2 * _RECORDS_PER_DOCUMENT
    assert {record.record.data["settlement-id"] for record in output.records} == {"12345678901"}
    assert all("dataEndTime" in record.record.data for record in output.records)

    # Each report resolves its own document exactly once and downloads it exactly once; the
    # CANCELLED and FATAL reports are filtered out of the listing and never reach getReport.
    for request in (first_document, first_download, second_document, second_download):
        http_mocker.assert_number_of_calls(request, 1)
    assert not [url for url in _requested_urls(http_mocker) if _CANCELLED_REPORT_ID in url or _FATAL_REPORT_ID in url]


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_done_settlement_report_when_read_then_document_url_resolved_immediately_before_download(
    http_mocker: HttpMocker,
) -> None:
    """
    Amazon signs the document URL with `X-Amz-Expires=300`. Resolving it in a separate parent stream
    minted the URL during partition generation and consumed it much later during partition read, so
    it expired (S3 403 "Request has expired") and every retry replayed the same dead URL. The
    download must be the request that immediately follows its `getReportDocument` call.
    """
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(
        _list_reports_request(),
        _list_reports_response([_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID)]),
    )
    _mock_report_chain(http_mocker, _DONE_REPORT_ID, _DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL)

    output = read_output(config_builder=_config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

    assert len(output.errors) == 0
    assert len(output.records) == _RECORDS_PER_DOCUMENT

    urls = [url for url in _requested_urls(http_mocker) if "/auth/" not in url]
    document_index = next(index for index, url in enumerate(urls) if f"documents/{_DONE_REPORT_DOCUMENT_ID}" in url)
    assert urls[document_index + 1] == _DONE_DOWNLOAD_URL


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_document_lookup_forbidden_once_when_read_then_retried_and_records_emitted(http_mocker: HttpMocker) -> None:
    """A transient 403 from `getReportDocument` (e.g. expired token) must be retried instead of failing the stream."""
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(_list_reports_request(), _list_reports_response([_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID)]))
    http_mocker.get(
        RequestBuilder.check_report_status_endpoint(_DONE_REPORT_ID).build(),
        build_response(_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID), status_code=HTTPStatus.OK),
    )
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


@HttpMocker()
def test_given_previous_sync_state_when_read_then_listing_resumes_at_previous_sync_end_and_reports_not_downloaded_again(
    http_mocker: HttpMocker,
) -> None:
    """
    Each sync must list reports created since the end of the previous sync, to the second. The checkpoint used to be
    truncated to a date, so the next sync re-listed every report created earlier that day and emitted all of its rows
    again; the stream has no primary key, so destinations could not remove them. The second sync starts from the state
    the first sync emitted, and its listing mock only matches `createdSince` equal to the first sync's exact end.
    """
    first_sync_at = NOW.add(hours=15, minutes=30, seconds=12)  # not midnight, so a date-only checkpoint would differ
    second_sync_at = first_sync_at.add(hours=18)
    start_date = first_sync_at.subtract(days=30)
    config_builder = config().with_start_date(start_date).without_end_date()

    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    first_listing = _list_reports_request(created_since=start_date, created_until=first_sync_at)
    second_listing = _list_reports_request(created_since=first_sync_at, created_until=second_sync_at)
    http_mocker.get(first_listing, _list_reports_response([_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID)]))
    http_mocker.get(second_listing, _list_reports_response([_report(_SECOND_DONE_REPORT_ID, "DONE", _SECOND_DONE_REPORT_DOCUMENT_ID)]))
    _, first_document, first_download = _mock_report_chain(http_mocker, _DONE_REPORT_ID, _DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL)
    _, second_document, second_download = _mock_report_chain(
        http_mocker, _SECOND_DONE_REPORT_ID, _SECOND_DONE_REPORT_DOCUMENT_ID, _SECOND_DONE_DOWNLOAD_URL
    )

    with freezegun.freeze_time(first_sync_at.isoformat()):
        first_sync = read_output(config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)
    assert len(first_sync.errors) == 0
    assert len(first_sync.records) == _RECORDS_PER_DOCUMENT
    assert _listing_checkpoint(first_sync) == first_sync_at.strftime("%Y-%m-%dT%H:%M:%SZ")

    first_sync_state = StateBuilder().with_stream_state(_STREAM_NAME, first_sync.most_recent_state.stream_state.__dict__).build()
    with freezegun.freeze_time(second_sync_at.isoformat()):
        second_sync = read_output(
            config_builder=config_builder, stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental, state=first_sync_state
        )
    assert len(second_sync.errors) == 0
    assert len(second_sync.records) == _RECORDS_PER_DOCUMENT
    assert _listing_checkpoint(second_sync) == second_sync_at.strftime("%Y-%m-%dT%H:%M:%SZ")

    for request in (first_listing, second_listing, first_document, first_download, second_document, second_download):
        http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_state_and_lookback_window_configured_when_read_then_reports_listed_from_checkpoint(http_mocker: HttpMocker) -> None:
    """
    `report_stream_lookback_window_in_hours` does not apply to this stream, as the user docs state. Re-listing a report
    downloads and emits all of its rows again, and the stream has no primary key to deduplicate them.
    """
    checkpoint = NOW.subtract(days=10)

    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    listing = _list_reports_request(created_since=checkpoint)
    http_mocker.get(listing, _list_reports_response([_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID)]))
    _, document_request, download_request = _mock_report_chain(http_mocker, _DONE_REPORT_ID, _DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL)

    output = read_output(
        config_builder=_config().with_report_stream_lookback_window_in_hours(6),
        stream_name=_STREAM_NAME,
        sync_mode=SyncMode.incremental,
        state=_state_with_listing_checkpoint(checkpoint),
    )

    assert len(output.errors) == 0
    assert len(output.records) == _RECORDS_PER_DOCUMENT
    for request in (listing, document_request, download_request):
        http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_period_in_days_shorter_than_window_when_read_then_each_report_downloaded_once(http_mocker: HttpMocker) -> None:
    """
    `period_in_days` must not split a report's partition into date windows. The window is never sent to Amazon, so
    each window used to run as its own job and download and emit the same document again: a 30-day window with
    `period_in_days=7` emitted every row five times.
    """
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(_list_reports_request(), _list_reports_response([_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID)]))
    report_request, document_request, download_request = _mock_report_chain(
        http_mocker, _DONE_REPORT_ID, _DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL
    )

    output = read_output(config_builder=_config().with_period_in_days(7), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

    assert len(output.errors) == 0
    assert len(output.records) == _RECORDS_PER_DOCUMENT
    http_mocker.assert_number_of_calls(report_request, 2)  # one job: the creation request, then one poll
    http_mocker.assert_number_of_calls(document_request, 1)
    http_mocker.assert_number_of_calls(download_request, 1)


@freezegun.freeze_time(NOW.isoformat())
@pytest.mark.parametrize("listed_status", ["IN_QUEUE", "IN_PROGRESS"])
@HttpMocker()
def test_given_report_still_processing_when_listed_then_polled_until_done_and_downloaded(
    listed_status: str, http_mocker: HttpMocker, mocker
) -> None:
    """
    A settlement report can still be processing when it is listed, with no `reportDocumentId` yet. The listing
    checkpoint moves past it either way, so skipping it would mean it is never listed again. The async retriever must
    poll it until `DONE` and then download it.
    """
    mocker.patch.object(AsyncJobOrchestrator, "_WAIT_TIME_BETWEEN_STATUS_UPDATE_IN_SECONDS", 0)
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(_list_reports_request(), _list_reports_response([_report(_IN_PROGRESS_REPORT_ID, listed_status)]))
    report_request = RequestBuilder.check_report_status_endpoint(_IN_PROGRESS_REPORT_ID).build()
    http_mocker.get(
        report_request,
        [
            build_response(_report(_IN_PROGRESS_REPORT_ID, listed_status), status_code=HTTPStatus.OK),  # job creation
            build_response(_report(_IN_PROGRESS_REPORT_ID, listed_status), status_code=HTTPStatus.OK),  # first poll
            build_response(_report(_IN_PROGRESS_REPORT_ID, "DONE", _IN_PROGRESS_REPORT_DOCUMENT_ID), status_code=HTTPStatus.OK),
        ],
    )
    document_request = RequestBuilder.get_document_download_url_endpoint(_IN_PROGRESS_REPORT_DOCUMENT_ID).build()
    download_request = RequestBuilder.download_document_endpoint(_IN_PROGRESS_DOWNLOAD_URL).build()
    http_mocker.get(document_request, _document_response(_IN_PROGRESS_REPORT_DOCUMENT_ID, _IN_PROGRESS_DOWNLOAD_URL))
    http_mocker.get(download_request, _download_response())

    output = read_output(config_builder=_config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

    assert len(output.errors) == 0
    assert len(output.records) == _RECORDS_PER_DOCUMENT
    http_mocker.assert_number_of_calls(report_request, 3)
    http_mocker.assert_number_of_calls(document_request, 1)
    http_mocker.assert_number_of_calls(download_request, 1)


@freezegun.freeze_time(NOW.isoformat())
@pytest.mark.parametrize(
    "report_id, processing_status",
    [
        pytest.param(_CANCELLED_REPORT_ID, "CANCELLED", id="cancelled"),
        pytest.param(_FATAL_REPORT_ID, "FATAL", id="fatal"),
    ],
)
@HttpMocker()
def test_given_report_without_document_when_listed_then_skipped_without_failing(
    report_id: str, processing_status: str, http_mocker: HttpMocker
) -> None:
    """
    `CANCELLED` and `FATAL` settlement reports never get a document. Amazon generates these reports itself, so a
    `FATAL` one cannot be retried; polling it would fail every sync. Only the listing is mocked, so any request for the
    report would fail the read.
    """
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(_list_reports_request(), _list_reports_response([_report(report_id, processing_status)]))

    output = read_output(config_builder=_config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

    assert len(output.records) == 0
    assert len(output.errors) == 0


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_state_from_before_documents_were_downloaded_when_read_then_full_window_listed_again(http_mocker: HttpMocker) -> None:
    """
    6.1.0 and earlier checkpointed the listing without downloading any document, so their state points past reports
    that were never emitted. The listing checkpoint moved from `dataEndTime` to `listedUntil`, so that old checkpoint
    is ignored and the full window is listed again, including reports the old state already has partitions for.
    """
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    listing = _list_reports_request(created_since=_START_DATE)
    http_mocker.get(listing, _list_reports_response([_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID)]))
    _, document_request, download_request = _mock_report_chain(http_mocker, _DONE_REPORT_ID, _DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL)

    output = read_output(
        config_builder=_config(),
        stream_name=_STREAM_NAME,
        sync_mode=SyncMode.incremental,
        state=_state_written_by_6_1_0(
            listing_start=_START_DATE.subtract(days=1), sync_at=NOW.subtract(hours=8), listed_report_ids=[_DONE_REPORT_ID]
        ),
    )

    assert len(output.errors) == 0
    assert len(output.records) == _RECORDS_PER_DOCUMENT
    for request in (listing, document_request, download_request):
        http_mocker.assert_number_of_calls(request, 1)
    assert _listing_checkpoint(output) == _END_DATE.strftime("%Y-%m-%dT%H:%M:%SZ")


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_more_reports_than_one_page_when_read_then_next_token_is_the_only_query_param(http_mocker: HttpMocker) -> None:
    """
    `getReports` returns the pagination token as `nextToken` (lower camel case), and rejects a request
    that sends it alongside `reportTypes`, `pageSize`, `createdSince` or `createdUntil` with
    `400 InvalidInput`. The token is an opaque cursor that already encodes those filters, so pages 2+
    must carry nothing else -- and the reports they return must still be downloaded, which is what
    proves the filters were not lost when they were dropped from the request.
    """
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)

    first_page = _list_reports_request()
    second_page = _list_reports_next_page_request(_NEXT_TOKEN)
    third_page = _list_reports_next_page_request(_NEXT_TOKEN_2)
    http_mocker.get(
        first_page,
        _list_reports_response([_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID)], next_token=_NEXT_TOKEN),
    )
    http_mocker.get(
        second_page,
        _list_reports_response([_report(_SECOND_DONE_REPORT_ID, "DONE", _SECOND_DONE_REPORT_DOCUMENT_ID)], next_token=_NEXT_TOKEN_2),
    )
    http_mocker.get(
        third_page,
        _list_reports_response([_report(_THIRD_DONE_REPORT_ID, "DONE", _THIRD_DONE_REPORT_DOCUMENT_ID)]),
    )

    _mock_report_chain(http_mocker, _DONE_REPORT_ID, _DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL)
    _, second_document, second_download = _mock_report_chain(
        http_mocker, _SECOND_DONE_REPORT_ID, _SECOND_DONE_REPORT_DOCUMENT_ID, _SECOND_DONE_DOWNLOAD_URL
    )
    _, third_document, third_download = _mock_report_chain(
        http_mocker, _THIRD_DONE_REPORT_ID, _THIRD_DONE_REPORT_DOCUMENT_ID, _THIRD_DONE_DOWNLOAD_URL
    )

    output = read_output(config_builder=_config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

    assert len(output.errors) == 0
    for request in (second_page, third_page, second_document, second_download, third_document, third_download):
        http_mocker.assert_number_of_calls(request, 1)
    assert len(output.records) == 3 * _RECORDS_PER_DOCUMENT


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_presigned_url_expired_once_when_read_then_url_reminted_and_records_emitted(http_mocker: HttpMocker) -> None:
    """
    If the pre-signed URL has expired by the time it is downloaded, S3 answers `403 Request has expired`.
    Replaying the same URL can never succeed, so the connector must resolve a fresh URL through
    `getReportDocument` and download that one instead.
    """
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(_list_reports_request(), _list_reports_response([_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID)]))
    http_mocker.get(
        RequestBuilder.check_report_status_endpoint(_DONE_REPORT_ID).build(),
        build_response(_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID), status_code=HTTPStatus.OK),
    )
    document_request = RequestBuilder.get_document_download_url_endpoint(_DONE_REPORT_DOCUMENT_ID).build()
    http_mocker.get(
        document_request,
        [
            _document_response(_DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL),
            _document_response(_DONE_REPORT_DOCUMENT_ID, _SECOND_DONE_DOWNLOAD_URL),
        ],
    )
    expired_download = RequestBuilder.download_document_endpoint(_DONE_DOWNLOAD_URL).build()
    fresh_download = RequestBuilder.download_document_endpoint(_SECOND_DONE_DOWNLOAD_URL).build()
    http_mocker.get(expired_download, _expired_url_response())
    http_mocker.get(fresh_download, _download_response())

    output = read_output(config_builder=_config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental)

    assert len(output.errors) == 0
    assert len(output.records) == _RECORDS_PER_DOCUMENT
    http_mocker.assert_number_of_calls(document_request, 2)
    http_mocker.assert_number_of_calls(expired_download, 1)
    http_mocker.assert_number_of_calls(fresh_download, 1)


@freezegun.freeze_time(NOW.isoformat())
@HttpMocker()
def test_given_presigned_url_always_rejected_when_read_then_stream_fails_without_emitting_error_body(http_mocker: HttpMocker) -> None:
    """
    Refreshing the URL is bounded. If S3 keeps rejecting fresh URLs, the stream must fail rather than loop
    forever or hand the 403 error body to the CSV decoder as if it were report data.
    """
    http_mocker.clear_all_matchers()
    mock_auth(http_mocker)
    http_mocker.get(_list_reports_request(), _list_reports_response([_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID)]))
    http_mocker.get(
        RequestBuilder.check_report_status_endpoint(_DONE_REPORT_ID).build(),
        build_response(_report(_DONE_REPORT_ID, "DONE", _DONE_REPORT_DOCUMENT_ID), status_code=HTTPStatus.OK),
    )
    document_request = RequestBuilder.get_document_download_url_endpoint(_DONE_REPORT_DOCUMENT_ID).build()
    http_mocker.get(document_request, _document_response(_DONE_REPORT_DOCUMENT_ID, _DONE_DOWNLOAD_URL))
    download_request = RequestBuilder.download_document_endpoint(_DONE_DOWNLOAD_URL).build()
    http_mocker.get(download_request, _expired_url_response())

    output = read_output(config_builder=_config(), stream_name=_STREAM_NAME, sync_mode=SyncMode.incremental, expecting_exception=True)

    assert len(output.records) == 0
    assert any("pre-signed URL was rejected" in error.trace.error.message for error in output.errors)
    # The initial resolution plus two refreshes, each followed by a download attempt.
    http_mocker.assert_number_of_calls(document_request, 3)
    http_mocker.assert_number_of_calls(download_request, 3)
