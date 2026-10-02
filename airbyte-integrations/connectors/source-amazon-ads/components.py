# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

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


_DUPLICATE_REPORT_ID_PATTERN = re.compile(r"duplicate of\s*:\s*([A-Za-z0-9-]+)", re.IGNORECASE)

_DUPLICATE_REPORT_REQUEST_ERROR_MESSAGE = (
    "Amazon detected duplicate report requests. This occurs when syncing the same report types "
    "with different time granularities simultaneously. To fix: create a separate source with only "
    "the needed report streams and set Number of concurrent threads to 2 for sequential processing."
)

logger = logging.getLogger("airbyte")


@dataclass
class DuplicateReportCreationRequester(HttpRequester):
    """
    Report creation requester that recovers from Amazon's HTTP 425 duplicate-report response.

    Amazon rejects a report creation POST with HTTP 425 and a body like
    "The Request is a duplicate of : <reportId>" when an identical report is already running.
    Instead of failing, this requester fetches the named report via GET /reporting/reports/{id}
    and returns that response as if it were the creation response, so the existing polling and
    download flow works unchanged. A 425 without a report ID still fails as a config error.
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
            raise AirbyteTracedException(
                message=_DUPLICATE_REPORT_REQUEST_ERROR_MESSAGE,
                internal_message=f"Report creation returned 425 without a report ID: {response.text}",
                failure_type=FailureType.config_error,
            )

        report_id = match.group(1)
        logger.info(f"Amazon rejected the report request as a duplicate of report {report_id}; reusing that report.")
        _, existing = self._http_client.send_request(
            http_method="GET",
            url=self._join_url(
                self.get_url_base(stream_state=stream_state, stream_slice=stream_slice),
                f"reporting/reports/{report_id}",
            ),
            request_kwargs={"stream": False},
            headers=self._request_headers(stream_state, stream_slice, next_page_token, request_headers),
            params={},
            log_formatter=log_formatter,
        )
        return existing
