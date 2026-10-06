# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod, Requester
from airbyte_cdk.sources.types import StreamSlice, StreamState
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


# Amazon report IDs are UUIDs. Matching only that shape keeps unexpected 425 wording from being
# mistaken for an ID and polled as a report that does not exist.
_DUPLICATE_REPORT_ID_PATTERN = re.compile(
    r"duplicate of\s*:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.IGNORECASE,
)

# A FAILED report never completes, so reusing it would only fail the job again.
_REUSABLE_REPORT_STATUSES = {"PENDING", "PROCESSING", "COMPLETED"}

# The configuration fields that decide which rows a report holds. `name` and `format` are left out:
# neither changes the rows, and Amazon is not known to treat them as part of a duplicate.
_REPORT_CONFIGURATION_FIELDS = ("adProduct", "reportTypeId", "timeUnit", "groupBy", "columns", "filters")

# A 425 that cannot be reused clears once the report it collided with finishes, which usually takes
# minutes. The orchestrator retries a failed creation with no delay, so the wait has to happen here.
_DUPLICATE_REPORT_MAX_ATTEMPTS = 4
_DUPLICATE_REPORT_RETRY_WAIT_SECONDS = 60

_UNUSABLE_DUPLICATE_REPORT_ERROR_MESSAGE = (
    "Amazon rejected the report request as a duplicate of a report that is still being generated, "
    "and that report could not be reused. This clears once that report finishes, so a later attempt should succeed."
)

logger = logging.getLogger("airbyte")


def _canonical(value: Any) -> Any:
    """Order-insensitive form of a configuration value, with null and an empty list treated alike."""
    if value is None:
        return []
    if isinstance(value, list):
        return sorted(json.dumps(item, sort_keys=True) for item in value)
    return value


def _report_mismatch(report: Mapping[str, Any], requested: Mapping[str, Any]) -> Optional[str]:
    """Name the first field where an existing report differs from a report request, or None if it matches."""
    for field in ("startDate", "endDate"):
        if str(report.get(field) or "").strip() != str(requested.get(field) or "").strip():
            return field
    configuration = report.get("configuration") or {}
    requested_configuration = requested.get("configuration") or {}
    for field in _REPORT_CONFIGURATION_FIELDS:
        if _canonical(configuration.get(field)) != _canonical(requested_configuration.get(field)):
            return f"configuration.{field}"
    return None


@dataclass
class DuplicateReportCreationRequester(Requester):
    """
    Report creation requester that recovers from Amazon's HTTP 425 duplicate-report response.

    Amazon rejects a report creation POST with HTTP 425 and a body like
    "The Request is a duplicate of : <reportId>" while a report it considers a duplicate is still being
    generated, for example when a sync attempt is retried after the previous attempt already requested it.
    The named report is reused only after looking it up and confirming it holds what this request asked for:
    same report type, time unit, columns, grouping, filters, and dates. #61652 reported Amazon flagging summary
    and daily requests of one report type as duplicates of each other, and reusing one for the other would
    silently sync the wrong rows. A reused report gets a stand-in creation response carrying its ID, so the
    polling requester picks it up and the download flow runs unchanged.

    A 425 that names no report, or names one that cannot be reused, is retried after a wait, since it clears
    once that report finishes. If it persists, the request fails with a transient error.

    `requester` and `report_requester` are built by the CDK like any HttpRequester, so they keep the request
    options, error handling, and test-read settings (logging, disabled retries) that the factory wires in.
    """

    requester: HttpRequester
    report_requester: HttpRequester

    def get_authenticator(self) -> DeclarativeAuthenticator:
        return self.requester.get_authenticator()

    def get_url(self, **kwargs: Any) -> str:
        return self.requester.get_url(**kwargs)

    def get_url_base(self, **kwargs: Any) -> str:
        return self.requester.get_url_base(**kwargs)

    def get_path(self, **kwargs: Any) -> str:
        return self.requester.get_path(**kwargs)

    def get_method(self) -> HttpMethod:
        return self.requester.get_method()

    def get_request_params(self, **kwargs: Any) -> Mapping[str, Any]:
        return self.requester.get_request_params(**kwargs)

    def get_request_headers(self, **kwargs: Any) -> Mapping[str, Any]:
        return self.requester.get_request_headers(**kwargs)

    def get_request_body_data(self, **kwargs: Any) -> Union[Mapping[str, Any], str]:
        return self.requester.get_request_body_data(**kwargs)

    def get_request_body_json(self, **kwargs: Any) -> Optional[Mapping[str, Any]]:
        return self.requester.get_request_body_json(**kwargs)

    def send_request(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Optional[requests.Response]:
        for attempt in range(1, _DUPLICATE_REPORT_MAX_ATTEMPTS + 1):
            response = self.requester.send_request(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
                path=path,
                request_headers=request_headers,
                request_params=request_params,
                request_body_data=request_body_data,
                request_body_json=request_body_json,
                log_formatter=log_formatter,
            )
            if response is None or response.status_code != 425:
                return response

            match = _DUPLICATE_REPORT_ID_PATTERN.search(response.text)
            if match is None:
                reason = "the response names no report"
            else:
                report_id = match.group(1)
                creation_response = self._build_duplicate_creation_response(report_id, response)
                reason = self._reuse_blocker(report_id, creation_response, stream_slice)
                if reason is None:
                    logger.info(f"Amazon rejected the report request as a duplicate of report {report_id}; reusing that report.")
                    return creation_response

            # Builder test reads disable retries so they fail fast; waiting here would undo that.
            if attempt == _DUPLICATE_REPORT_MAX_ATTEMPTS or self.requester.disable_retries:
                break
            logger.warning(
                f"Amazon rejected the report request as a duplicate and {reason}. "
                f"Requesting the report again in {_DUPLICATE_REPORT_RETRY_WAIT_SECONDS} seconds "
                f"(attempt {attempt} of {_DUPLICATE_REPORT_MAX_ATTEMPTS})."
            )
            time.sleep(_DUPLICATE_REPORT_RETRY_WAIT_SECONDS)

        # Not a config error: the duplicate clears once the earlier report finishes, and a config
        # error would stop every report job in the stream and skip the platform's retries.
        raise AirbyteTracedException(
            message=_UNUSABLE_DUPLICATE_REPORT_ERROR_MESSAGE,
            internal_message=f"Report creation returned 425 after {attempt} attempt(s); {reason}. Response: {response.text}",
            failure_type=FailureType.transient_error,
        )

    def _reuse_blocker(self, report_id: str, creation_response: requests.Response, stream_slice: Optional[StreamSlice]) -> Optional[str]:
        """
        Look up the report a 425 names and say why it cannot stand in for this request, or None if it can.

        The lookup is the polling requester's request, sent with the interpolation context
        AsyncHttpJobRepository builds from a creation response, so it is the first status check polling
        would make. `report_lookup_error_handler` retries what polling retries but returns 403 and 404
        here, so a report this client cannot read is declined instead of failing the stream.
        """
        lookup_slice = StreamSlice(
            partition=stream_slice.partition if stream_slice else {},
            cursor_slice=stream_slice.cursor_slice if stream_slice else {},
            extra_fields={
                **(stream_slice.extra_fields if stream_slice else {}),
                "creation_response": {
                    **creation_response.json(),
                    "headers": creation_response.headers,
                    "request": creation_response.request,
                },
            },
        )
        report_response = self.report_requester.send_request(stream_slice=lookup_slice)
        if report_response is None or report_response.status_code != 200:
            status_code = report_response.status_code if report_response is not None else None
            return f"looking up report {report_id} returned HTTP {status_code}"

        report = report_response.json()
        if report.get("status") not in _REUSABLE_REPORT_STATUSES:
            return f"report {report_id} has status {report.get('status')}"

        try:
            requested = json.loads(creation_response.request.body)
        except (TypeError, ValueError):
            return f"the request body could not be compared with report {report_id}"
        mismatch = _report_mismatch(report, requested)
        if mismatch is not None:
            return f"report {report_id} has a different {mismatch} than this request"
        return None

    @staticmethod
    def _build_duplicate_creation_response(report_id: str, duplicate_response: requests.Response) -> requests.Response:
        """
        Stand in for the creation response Amazon returns when it accepts a report request.

        The polling requester reads `creation_response['reportId']` and copies the profile scope header
        from `creation_response.request`, so this keeps the 425's request, which is the original POST.
        """
        creation_response = requests.Response()
        creation_response.status_code = 200
        creation_response.headers["Content-Type"] = "application/json"
        creation_response.url = duplicate_response.url
        creation_response.request = duplicate_response.request
        creation_response.encoding = "utf-8"
        creation_response._content = json.dumps({"reportId": report_id}).encode("utf-8")
        return creation_response
