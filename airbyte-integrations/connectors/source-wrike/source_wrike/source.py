#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from pendulum import DateTime


# Basic full refresh stream
class WrikeStream(HttpStream, ABC):
    """
    Wrike API Reference: https://developers.wrike.com/overview/
    """

    primary_key = "id"
    url_base = ""

    def __init__(self, wrike_instance: str, **kwargs):
        super().__init__(**kwargs)
        self.url_base = f"https://{wrike_instance}/api/v4/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        nextPageToken = response.json().get("nextPageToken")

        if nextPageToken:
            return {"nextPageToken": nextPageToken}
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        for record in response.json()["data"]:
            yield record

    def path(self, **kwargs) -> str:
        """
        This one is tricky, the API path is the class name by default. Airbyte will load  `url_base`/`classname` by
        default, like https://app-us2.wrike.com/api/v4/tasks if the class name is Tasks
        """
        return self.__class__.__name__.lower()


class Tasks(WrikeStream):
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        return next_page_token or {"fields": "[customFields,parentIds,authorIds,responsibleIds,description,briefDescription,superTaskIds]"}


class Customfields(WrikeStream):
    pass


class Contacts(WrikeStream):
    pass


class Workflows(WrikeStream):
    pass


def to_utc_z(date: DateTime):
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


class Comments(WrikeStream):
    def __init__(self, start_date: DateTime, **kwargs):
        self._start_date = start_date
        super().__init__(**kwargs)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Yields a list of the beginning timestamps of each 7 days period between the start date and now,
        as the comments endpoint limits the requests for 7 days intervals.
        """
        start_date = self._start_date
        now = pendulum.now()

        while start_date <= now:
            end_date = start_date + pendulum.duration(days=7)
            yield {"start": to_utc_z(start_date)}
            start_date = end_date

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        slice_params = {"updatedDate": '{"start":"' + stream_slice["start"] + '"}'}
        return next_page_token or slice_params


class Folders(WrikeStream):
    pass


# Source


class SourceWrike(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        try:
            headers = {
                "Accept": "application/json",
            } | TokenAuthenticator(token=config["access_token"]).get_auth_header()

            resp = requests.get(f"https://{config['wrike_instance']}/api/v4/version", headers=headers)
            resp.raise_for_status()
            return True, None

        except requests.exceptions.RequestException as e:
            error = e.response.json()
            message = error.get("errorDescription") or error.get("error")
            return False, message

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        start_date = pendulum.parse(config.get("start_date")) if config.get("start_date") else pendulum.now().subtract(days=7)

        args = {"authenticator": TokenAuthenticator(token=config["access_token"]), "wrike_instance": config["wrike_instance"]}
        return [
            Tasks(**args),
            Customfields(**args),
            Contacts(**args),
            Workflows(**args),
            Folders(**args),
            Comments(start_date=start_date, **args),
        ]
