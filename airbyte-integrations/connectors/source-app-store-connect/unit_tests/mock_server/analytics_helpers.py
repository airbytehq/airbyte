# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Literal, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import error_response, fixture_response, tabular_response
from .utils import read_output


APP_ID = "app-1"
REQUEST_ID = "request-1"
REPORT_ID = "report-1"
INSTANCE_ID = "instance-1"
SEGMENT_ID = "segment-1"
DOWNLOAD_URL = "https://example.s3.amazonaws.com/app-store-connect/report.csv.gz?signature=test"
PAGE_TWO_CURSOR = "PAGE_TWO"

Stage = Literal["request", "report", "instance", "segment", "detail", "download"]
Family = Literal["installations", "downloads"]


@dataclass(frozen=True)
class AnalyticsSpec:
    stage: Stage
    family: Family
    historical: bool


ANALYTICS_SPECS = {
    "analytics_report_requests_ongoing": AnalyticsSpec("request", "installations", False),
    "analytics_report_requests_historical": AnalyticsSpec("request", "installations", True),
    "analytics_installations_reports": AnalyticsSpec("report", "installations", False),
    "analytics_installations_instances": AnalyticsSpec("instance", "installations", False),
    "analytics_installations_segments": AnalyticsSpec("segment", "installations", False),
    "analytics_installations_segment_details": AnalyticsSpec("detail", "installations", False),
    "app_store_installations_and_deletions": AnalyticsSpec("download", "installations", False),
    "analytics_installations_reports_historical": AnalyticsSpec("report", "installations", True),
    "analytics_installations_instances_historical": AnalyticsSpec("instance", "installations", True),
    "analytics_installations_segments_historical": AnalyticsSpec("segment", "installations", True),
    "analytics_installations_segment_details_historical": AnalyticsSpec("detail", "installations", True),
    "app_store_installations_and_deletions_historical": AnalyticsSpec("download", "installations", True),
    "analytics_app_download_reports": AnalyticsSpec("report", "downloads", False),
    "analytics_app_download_instances": AnalyticsSpec("instance", "downloads", False),
    "analytics_app_download_segments": AnalyticsSpec("segment", "downloads", False),
    "analytics_app_download_segment_details": AnalyticsSpec("detail", "downloads", False),
    "app_download": AnalyticsSpec("download", "downloads", False),
    "analytics_app_download_reports_historical": AnalyticsSpec("report", "downloads", True),
    "analytics_app_download_instances_historical": AnalyticsSpec("instance", "downloads", True),
    "analytics_app_download_segments_historical": AnalyticsSpec("segment", "downloads", True),
    "analytics_app_download_segment_details_historical": AnalyticsSpec("detail", "downloads", True),
    "app_download_historical": AnalyticsSpec("download", "downloads", True),
}


def processing_date() -> str:
    return "2024-01-03"


def analytics_config() -> ConfigBuilder:
    return ConfigBuilder().with_value("analytics_reports_start_date", "2024-01-01")


def analytics_state(stream_name: str):
    return StateBuilder().with_stream_state(stream_name, {"processing_date": "2024-01-02"}).build()


def _access_type(spec: AnalyticsSpec) -> str:
    return "ONE_TIME_SNAPSHOT" if spec.historical else "ONGOING"


def _report_name(spec: AnalyticsSpec) -> str:
    if spec.family == "installations":
        return "App Store Installation and Deletion Standard"
    return "App Downloads Standard"


def _fixture_name(spec: AnalyticsSpec, stage: Stage) -> str:
    if stage == "request":
        return "analytics_report_requests_historical" if spec.historical else "analytics_report_requests_ongoing"
    return next(
        stream_name for stream_name, candidate in ANALYTICS_SPECS.items() if candidate == AnalyticsSpec(stage, spec.family, spec.historical)
    )


def _register_collection(
    http_mocker: HttpMocker,
    request: RequestBuilder,
    fixture_name: str,
    is_target: bool,
    paginate_target: bool,
    target_response: Optional[HttpResponse],
) -> None:
    if is_target and target_response:
        http_mocker.get(request.build(), target_response)
        return

    if is_target and paginate_target:
        next_url = f"{request.url}?cursor={PAGE_TWO_CURSOR}"
        first_request = request.build()
        second_request = request.with_cursor(PAGE_TWO_CURSOR).build()
        http_mocker.get(first_request, fixture_response(fixture_name, next_url=next_url))
        http_mocker.get(second_request, fixture_response(fixture_name, id_suffix="-page-2"))
        return

    http_mocker.get(request.build(), fixture_response(fixture_name))


def mock_analytics_stream(
    http_mocker: HttpMocker,
    stream_name: str,
    paginate_target: bool = False,
    target_response: Optional[HttpResponse] = None,
) -> None:
    spec = ANALYTICS_SPECS[stream_name]
    access_type = _access_type(spec)

    http_mocker.get(
        RequestBuilder.apps_endpoint().build(),
        fixture_response("list_id_apps"),
    )

    request_builder = RequestBuilder.analytics_report_requests_endpoint(APP_ID).with_query_param("filter[accessType]", access_type)
    _register_collection(
        http_mocker,
        request_builder,
        _fixture_name(spec, "request"),
        spec.stage == "request",
        paginate_target,
        target_response,
    )
    if spec.stage == "request":
        return

    request_builder = RequestBuilder.analytics_reports_endpoint(REQUEST_ID).with_query_param("filter[name]", _report_name(spec))
    _register_collection(
        http_mocker,
        request_builder,
        _fixture_name(spec, "report"),
        spec.stage == "report",
        paginate_target,
        target_response,
    )
    if spec.stage == "report":
        return

    request_builder = RequestBuilder.analytics_instances_endpoint(REPORT_ID).with_query_param("filter[granularity]", "DAILY")
    _register_collection(
        http_mocker,
        request_builder,
        _fixture_name(spec, "instance"),
        spec.stage == "instance",
        paginate_target,
        target_response,
    )
    if spec.stage == "instance":
        return

    request_builder = RequestBuilder.analytics_segments_endpoint(INSTANCE_ID)
    _register_collection(
        http_mocker,
        request_builder,
        _fixture_name(spec, "segment"),
        spec.stage == "segment",
        paginate_target,
        target_response,
    )
    if spec.stage == "segment":
        return

    segment_request = RequestBuilder.analytics_segment_endpoint(SEGMENT_ID).build()
    if spec.stage == "detail" and target_response:
        http_mocker.get(segment_request, target_response)
    else:
        http_mocker.get(
            segment_request,
            fixture_response(_fixture_name(spec, "detail")),
        )
    if spec.stage == "detail":
        return

    http_mocker.get(
        RequestBuilder.download_endpoint(DOWNLOAD_URL).build(),
        target_response or tabular_response(stream_name),
    )


def ignored_analytics_response(stream_name: str) -> HttpResponse:
    status = HTTPStatus.NOT_FOUND if ANALYTICS_SPECS[stream_name].stage == "download" else HTTPStatus.FORBIDDEN
    return error_response(status)


def expected_record_id(stream_name: str) -> str:
    return {
        "request": REQUEST_ID,
        "report": REPORT_ID,
        "instance": INSTANCE_ID,
        "segment": SEGMENT_ID,
        "detail": SEGMENT_ID,
    }[ANALYTICS_SPECS[stream_name].stage]


def read_analytics_stream(
    http_mocker: HttpMocker,
    stream_name: str,
    *,
    paginate: bool = False,
    incremental: bool = False,
    ignored_error: bool = False,
) -> EntrypointOutput:
    mock_analytics_stream(
        http_mocker,
        stream_name,
        paginate_target=paginate,
        target_response=ignored_analytics_response(stream_name) if ignored_error else None,
    )
    return read_output(
        analytics_config(),
        stream_name,
        SyncMode.incremental if incremental else SyncMode.full_refresh,
        analytics_state(stream_name) if incremental else None,
    )
