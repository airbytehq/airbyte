# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.types import StreamSlice, StreamState
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


# Amazon report IDs are UUIDs. Matching only that shape keeps unexpected 425 wording from being
# mistaken for an ID and polled as a report that does not exist.
_DUPLICATE_REPORT_ID_PATTERN = re.compile(
    r"duplicate of\s*:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.IGNORECASE,
)

_UNIDENTIFIED_DUPLICATE_REPORT_ERROR_MESSAGE = (
    "Amazon rejected the report request as a duplicate of a report that is still being generated, "
    "but did not say which report. This clears once that report finishes, so a later attempt should succeed."
)

logger = logging.getLogger("airbyte")


@dataclass
class DuplicateReportCreationRequester(HttpRequester):
    """
    Report creation requester that recovers from Amazon's HTTP 425 duplicate-report response.

    Amazon rejects a report creation POST with HTTP 425 and a body like
    "The Request is a duplicate of : <reportId>" while an identical report is still being generated,
    for example when a sync attempt is retried after the previous attempt already requested it.
    Instead of failing, this requester returns a stand-in creation response carrying that report ID,
    so the polling requester picks up the existing report and the download flow runs unchanged.
    A 425 that names no report raises a transient error.
    """

    request_headers: Optional[Mapping[str, str]] = None
    request_body_json: Optional[Mapping[str, Any]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        # HttpRequester has no request_headers/request_body_json fields, so the custom-component
        # factory leaves them as plain attributes instead of building a request options provider.
        # Build one here or the manifest's scope header and report body would be silently dropped.
        self._request_options_provider = InterpolatedRequestOptionsProvider(
            config=self.config,
            parameters=parameters,
            request_headers=self.request_headers,
            request_body_json=self.request_body_json,
        )

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
        response = super().send_request(
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
            # Not a config error: the duplicate clears once the earlier report finishes, and a
            # config error would stop every report job in the stream and skip the platform's retries.
            raise AirbyteTracedException(
                message=_UNIDENTIFIED_DUPLICATE_REPORT_ERROR_MESSAGE,
                internal_message=f"Report creation returned 425 without a report ID: {response.text}",
                failure_type=FailureType.transient_error,
            )

        report_id = match.group(1)
        logger.info(f"Amazon rejected the report request as a duplicate of report {report_id}; reusing that report.")
        return self._build_duplicate_creation_response(report_id, response)

    @staticmethod
    def _build_duplicate_creation_response(report_id: str, duplicate_response: requests.Response) -> requests.Response:
        """
        Stand in for the creation response Amazon returns when it accepts a report request.

        The polling requester reads `creation_response['reportId']` and copies the profile scope header
        from `creation_response.request`, so this keeps the 425's request, which is the original POST.
        Leaving the first status check to the polling requester, rather than fetching the report here,
        runs it under `report_polling_error_handler`, which retries Amazon's transient 401s.
        """
        creation_response = requests.Response()
        creation_response.status_code = 200
        creation_response.headers["Content-Type"] = "application/json"
        creation_response.url = duplicate_response.url
        creation_response.request = duplicate_response.request
        creation_response.encoding = "utf-8"
        creation_response._content = json.dumps({"reportId": report_id}).encode("utf-8")
        return creation_response
