#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import csv
import io
from dataclasses import dataclass
from typing import Any, Callable, Generator, Mapping, MutableMapping, Optional, Union

import requests

from airbyte_cdk import AirbyteTracedException, Decoder, FailureType
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.types import StreamSlice, StreamState


@dataclass
class CustomDecoder(Decoder):
    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        fp = io.StringIO(response.text)
        reader = csv.DictReader(fp)
        for record in reader:
            yield record


@dataclass
class ContentOwnerRequester(HttpRequester):
    """
    Custom requester that conditionally adds the onBehalfOfContentOwner parameter
    only when content_owner_id is provided in the config.
    """

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = super().get_request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        content_owner_id = self.config.get("content_owner_id")
        if content_owner_id:
            params["onBehalfOfContentOwner"] = content_owner_id
        return params


@dataclass
class JobRequester(ContentOwnerRequester):
    """
    Sends request to create a report job if it doesn't exist yet.
    Extends ContentOwnerRequester to conditionally add onBehalfOfContentOwner parameter.
    """

    JOB_NAME = "Airbyte reporting job"

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
            stream_state,
            stream_slice,
            next_page_token,
            path,
            request_headers,
            request_params,
            request_body_data,
            request_body_json,
            log_formatter,
        )

        response_json = response.json()
        if "jobs" not in response_json:
            error_message = "YouTube Reporting API did not return expected 'jobs' data. "
            if "error" in response_json:
                error_details = response_json["error"]
                error_message += f"API Error: {error_details.get('message', str(error_details))}. "
            error_message += (
                "This may indicate that your Google account does not have a YouTube channel associated with it, "
                "or the OAuth credentials do not have the required YouTube Analytics permissions. "
                "If you manage multiple YouTube channels, try specifying a 'content_owner_id' in the connector configuration."
            )
            raise AirbyteTracedException(message=error_message, failure_type=FailureType.config_error)

        stream_job = [r for r in response_json["jobs"] if r["reportTypeId"] == self._parameters["report_type_id"]]

        if not stream_job:
            self._http_client.send_request(
                http_method="post",
                url=self._get_url(
                    path=path,
                    stream_state=stream_state,
                    stream_slice=stream_slice,
                    next_page_token=next_page_token,
                ),
                request_kwargs={"stream": self.stream_response},
                headers=self._request_headers(stream_state, stream_slice, next_page_token, request_headers),
                json={"name": self.JOB_NAME, "reportTypeId": self._parameters["report_id"]},
                dedupe_query_params=True,
                log_formatter=log_formatter,
                exit_on_rate_limit=self._exit_on_rate_limit,
            )
            response = super().send_request(
                stream_state,
                stream_slice,
                next_page_token,
                path,
                request_headers,
                request_params,
                request_body_data,
                request_body_json,
                log_formatter,
            )

        return response


class ReportsStateMigration(StateMigration):
    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return stream_state.get("state") or stream_state.get("date")

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if stream_state.get("date"):
            # old format state before migration to low code
            cursor_value = str(stream_state["date"])
            stream_state = {
                "state": {"date": cursor_value},
                "parent_state": {"report": {"state": {"date": cursor_value}, "lookback_window": 0}},
            }
            return stream_state

        cursor_value = stream_state["state"]
        cursor_value["date"] = str(cursor_value["date"])
        stream_state["parent_state"]["report"]["state"] = cursor_value
        stream_state["parent_state"]["report"]["lookback_window"] = 0
        return stream_state
