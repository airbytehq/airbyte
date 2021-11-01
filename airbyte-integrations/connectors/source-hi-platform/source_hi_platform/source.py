#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import base64
from abc import ABC
from typing import (
    Any,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
)
from urllib.parse import parse_qs, urlparse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class HiPlatformStream(HttpStream, ABC):
    """Hi Platform base stream."""

    max_retries = None
    url_base = "https://api.directtalk.com.br/1.9/info/"

    def __init__(self, start_date: int, **kwargs):
        """Initialize HiPlatformStream.

        Args:
            start_date (int): start date in unix time
            kwargs: extra args
        """
        super().__init__(**kwargs)
        self._start_date = start_date

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """Return the header X-Rate-Limit-Reset value as backoff time.

        Args:
            response (requests.Response): response

        Returns:
            Optional[float]: backoff time in seconds
        """
        return response.headers["X-Rate-Limit-Reset"]


class IncrementalHiPlatformStream(HiPlatformStream, ABC):
    """Base class for incremental streams."""

    page_size = 1000
    state_checkpoint_interval = None

    def next_page_token(
        self, response: requests.Response,
    ) -> Optional[Mapping[str, Any]]:
        """Handle pagination and return the next page.

        Args:
            response (requests.Response): raw response

        Returns:
            Optional[Mapping[str, Any]]: token
        """
        current_page = self._extract_page_number_from_url(response.url)
        next_page_link = response.links.get("Next") or response.links.get(
            "Last",
        )

        next_page = self._extract_page_number_from_url(next_page_link["url"])

        if current_page < next_page:
            return {"pageNumber": next_page}

        return None

    def stream_slices(  # noqa: WPS234
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, any]]]:
        """Generate slices of 30 days periods, a requirement from API.

        Args:
            sync_mode (SyncMode): sync mode.
            cursor_field (List[str], optional): cursor field.
            stream_state (Mapping[str, Any], optional): stream state.

        Returns:
            Iterable[Optional[Mapping[str, any]]]: stream slices
        """
        api_max_range_days = 31
        extraction_end_date = pendulum.today(pendulum.UTC).subtract(seconds=1)

        slice_start_date = self._start_date
        if stream_state:
            slice_start_date = stream_state.get(self.cursor_field)
            slice_start_date = slice_start_date + 1

        slice_start_date = pendulum.from_timestamp(slice_start_date)

        slices = []

        while slice_start_date < extraction_end_date:
            slice_end_date = slice_start_date.add(days=api_max_range_days)
            slice_end_date = slice_end_date.subtract(seconds=1)
            slice_end_date = min(slice_end_date, extraction_end_date)

            slices.append(
                {
                    "start_date": slice_start_date.int_timestamp,
                    "end_date": slice_end_date.int_timestamp,
                },
            )

            slice_start_date = slice_end_date.add(seconds=1)

        return slices

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Extract state from response using the cursor_field.

        Args:
            current_stream_state (MutableMapping[str, Any]): current state
            latest_record (Mapping[str, Any]): latest record

        Returns:
            Mapping[str, Any]: updated state
        """
        return {
            self.cursor_field: max(
                latest_record.get(self.cursor_field, 0),
                current_stream_state.get(self.cursor_field, 0),
            ),
        }

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """Generate needed request params for incremental extraction.

        Args:
            stream_state (Mapping[str, Any]): stream state
            stream_slice (Mapping[str, any], optional): stream slice.
            next_page_token (Mapping[str, Any], optional): next page token.

        Returns:
            MutableMapping[str, Any]: request params
        """
        request_params = {
            "startDate": stream_slice["start_date"],
            "endDate": stream_slice["end_date"],
            "pageNumber": 1,
            "pageSize": self.page_size,
        }

        if next_page_token:
            request_params.update(next_page_token)

        return request_params

    def parse_response(
        self, response: requests.Response, **kwargs,
    ) -> Iterable[Mapping]:
        """Process raw response.

        Args:
            response (requests.Response): raw response
            kwargs: extra args

        Yields:
            Iterator[Iterable[Mapping]]: parsed records
        """
        yield from response.json()

    def _extract_page_number_from_url(self, url: str) -> Mapping[str, Any]:
        parsed_url = parse_qs(urlparse(url).query)

        return int(parsed_url.get("pageNumber")[0])


class Contacts(IncrementalHiPlatformStream):
    """Contacts stream."""

    cursor_field = "contactFinishedDate"
    primary_key = "protocolNumber"
    date_info_param = "contactFinished"

    def path(self, **kwargs) -> str:
        """Return API endpoint.

        Args:
            kwargs: args

        Returns:
            str: path
        """
        return "contacts"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """Generate needed request params for incremental extraction.

        Args:
            stream_state (Mapping[str, Any]): stream state
            stream_slice (Mapping[str, any], optional): stream slice.
            next_page_token (Mapping[str, Any], optional): next page token.

        Returns:
            MutableMapping[str, Any]: request params
        """
        request_params = super().request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        request_params["dateInfo"] = self.date_info_param

        return request_params


class AgentEvents(IncrementalHiPlatformStream):
    """Agent Events stream."""

    cursor_field = "date"
    primary_key = None

    def path(self, **kwargs) -> str:
        """Return API endpoint.

        Args:
            kwargs: args

        Returns:
            str: path
        """
        return "reports/platform/agentevents"


class BasicApiTokenAuthenticator(TokenAuthenticator):
    """Basic Authorization header."""

    def __init__(self, login: str, password: str):
        """Initialize BasicApiTokenAuthenticator.

        Args:
            login (str): api login
            password (str): api password
        """
        concatenated_credential = "{0}:{1}".format(login, password)
        token = base64.b64encode(concatenated_credential.encode("utf-8"))
        super().__init__(token.decode("utf-8"), auth_method="Basic")


class SourceHiPlatform(AbstractSource):
    """Hi Platform Source."""

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """Try to login using supplied credentials.

        Args:
            logger ([type]): logger object
            config ([type]): config object conforming to connector's spec.json

        Returns:
            Tuple[bool, any]: (True, None) if the input config can be used to
                                connect to the API successfully,
                                (False, error) otherwise.
        """
        authenticator = self._init_authenticator(config)
        auth_exception = None
        request_date = pendulum.now().int_timestamp

        try:
            next(
                Contacts(
                    request_date, authenticator=authenticator,
                ).read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_slice={
                        "start_date": request_date,
                        "end_date": request_date,
                    },
                ),
                None,
            )
        except Exception as exc:
            auth_exception = exc

        return auth_exception is None, auth_exception

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Return streams list.

        Args:
            config (Mapping[str, Any]): config object
                                        conforming to the connector's spec.json

        Returns:
            List[Stream]: [description]
        """
        start_date_in_epoch = pendulum.parse(config["start_date"])
        start_date_in_epoch = start_date_in_epoch.int_timestamp

        auth = self._init_authenticator(config)

        return [
            Contacts(start_date_in_epoch, authenticator=auth),
            AgentEvents(start_date_in_epoch, authenticator=auth),
        ]

    def _init_authenticator(
        self, config: Mapping[str, Any]
    ) -> TokenAuthenticator:
        return BasicApiTokenAuthenticator(
            login=config["login"],
            password=config["password"],
        )
