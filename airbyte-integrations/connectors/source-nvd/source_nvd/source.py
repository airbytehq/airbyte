#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
TIME_FORMAT_LAST_MODIFIED_RECORD_WITHOUT_TIMEZONE_INFORMATION = TIME_FORMAT + ".%f"
TIME_FORMAT_LAST_MODIFIED_RECORD = TIME_FORMAT_LAST_MODIFIED_RECORD_WITHOUT_TIMEZONE_INFORMATION + "%z"


class NvdAuthenticator(TokenAuthenticator):
    def __init__(self, token: str):
        self._auth_header = "apiKey"
        self._token = token

    @property
    def token(self) -> str:
        return self._token


class NvdStream(HttpStream, IncrementalMixin, ABC):
    url_base = "https://services.nvd.nist.gov/rest/json/"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.start_date = datetime.strptime(config["modStartDate"], TIME_FORMAT)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        reponse_json = response.json()

        # If there are more pages to be retrieved
        if reponse_json["startIndex"] + reponse_json["resultsPerPage"] < reponse_json["totalResults"]:
            return {"startIndex": reponse_json["startIndex"] + reponse_json["resultsPerPage"]}

    def should_retry(self, response: requests.Response) -> bool:
        # NVD sends a 403 when being rate limited, so retry 403s
        return response.status_code == 429 or response.status_code == 403 or 500 <= response.status_code < 600

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        # Define a custom backoff time because with the default exponential backoff, 403's are not retried
        return 6

    @property
    def max_retries(self) -> int:
        # Increase number of retries a bit since the NVD API is weird with rate limiting sometimes
        return 10

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {}
        params["lastModStartDate"] = stream_slice["start_date"].strftime(TIME_FORMAT_LAST_MODIFIED_RECORD_WITHOUT_TIMEZONE_INFORMATION)
        params["lastModEndDate"] = stream_slice["end_date"].strftime(TIME_FORMAT_LAST_MODIFIED_RECORD_WITHOUT_TIMEZONE_INFORMATION)

        # Add pagination token to parameters
        if next_page_token is not None:
            params.update(**next_page_token)

        return params

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, Any]]:
        """
        Returns a list of day chunks between the start date and utc-now.
        """
        dates = []
        span = timedelta(days=1)
        while start_date < datetime.now(timezone.utc):
            dates.append({"start_date": start_date, "end_date": start_date + span})
            start_date += span
        return dates

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # If the stream state is set to a date, we use that, otherwise, use the start date
        # given by the user in the configuration of the source
        start_date = (
            datetime.strptime(stream_state[self.cursor_field], TIME_FORMAT_LAST_MODIFIED_RECORD)
            if stream_state and self.cursor_field in stream_state
            else self.start_date.astimezone(timezone.utc)
        )
        return self._chunk_date_range(start_date)

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.isoformat(timespec="milliseconds")}
        else:
            return {self.cursor_field: self.start_date.astimezone(timezone.utc).isoformat(timespec="milliseconds")}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], TIME_FORMAT_LAST_MODIFIED_RECORD)

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            latest_record_date = datetime.strptime(record[self.cursor_field], TIME_FORMAT_LAST_MODIFIED_RECORD)
            if self._cursor_value:
                self._cursor_value = max(self._cursor_value, latest_record_date)
            else:
                self._cursor_value = latest_record_date
            yield record


class Cves(NvdStream):
    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)

    primary_key = "id"
    cursor_field = "last_modified"
    _cursor_value = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "cves/2.0"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        results = response.json()["vulnerabilities"]

        # Add CVE ID and last modified date at root level
        for result in results:
            result["id"] = result["cve"]["id"]
            result["last_modified"] = (
                datetime.strptime(result["cve"]["lastModified"], TIME_FORMAT_LAST_MODIFIED_RECORD_WITHOUT_TIMEZONE_INFORMATION)
                .replace(tzinfo=timezone.utc)
                .isoformat(timespec="milliseconds")
            )
            yield result


class Cpes(NvdStream):
    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)

    primary_key = "id"
    cursor_field = "last_modified"
    _cursor_value = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "cpes/2.0"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        results = response.json()["products"]

        # Add CPE ID and last modified date at root level
        for result in results:
            result["id"] = result["cpe"]["cpeNameId"]
            result["last_modified"] = (
                datetime.strptime(result["cpe"]["lastModified"], TIME_FORMAT_LAST_MODIFIED_RECORD_WITHOUT_TIMEZONE_INFORMATION)
                .replace(tzinfo=timezone.utc)
                .isoformat(timespec="milliseconds")
            )
            yield result


class SourceNvd(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        # Input validation
        try:
            start = datetime.strptime(config["modStartDate"], TIME_FORMAT)
            if start > datetime.utcnow():
                return False, "Start date cannot be in the future"
        except ValueError:
            return False, f"Invalid start date format, use the format {TIME_FORMAT}"

        # Check if API is online
        try:
            if "apiKey" in config:
                auth = NvdAuthenticator(config["apiKey"])
            else:
                auth = None
            stream = Cves(config=config, authenticator=auth)
            records = stream.read_records(
                sync_mode=SyncMode.full_refresh, stream_slice={"start_date": datetime(2023, 1, 3), "end_date": datetime(2023, 1, 6)}
            )
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        if "apiKey" in config:
            auth = NvdAuthenticator(config["apiKey"])
        else:
            auth = None
        return [Cves(config=config, authenticator=auth), Cpes(config=config, authenticator=auth)]
