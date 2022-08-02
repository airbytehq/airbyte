#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import contextlib
import datetime
import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class BasicAuthenticator(TokenAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"{self._token}"}


class Links(HttpStream, ABC):

    url_base = "https://api.short.io/api/"
    limit = 150
    primary_key = "idString"
    before_id = None
    domain_id = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        links = json.loads(response.text)["links"]
        try:
            earliest_id_string = sorted(links, key=lambda k: k["createdAt"], reverse=False)[0]["idString"]
            if self.before_id != earliest_id_string:
                self.before_id = earliest_id_string
                return earliest_id_string
            else:
                return None
        except IndexError:
            return None

    def request_params(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            "limit": self.limit,
            "domain_id": self.domain_id,
            "before": next_page_token or None,
        }

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        # Get all the links
        return "links"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        The short.io API can be inconsistent in its inclusion of UTM parameters.
        Here, we check if they've been provided and if they haven't, attempt to extract it from the original url.
        """
        utm_response_fields_to_utm_params = {
            # Passing secondary UTM Campaign in order to capture either or of the 2 args.
            "utmSource": "utm_source",
            "utmMedium": "utm_medium",
            "utmCampaign": "utm_campaign",
            "utmCampaignId": "utm_id",
            "utmTerm": "utm_term",
            "utmContent": "utm_content",
        }
        links = json.loads(response.text)["links"]
        for item in links:
            for resp_field, param in utm_response_fields_to_utm_params.items():
                if resp_field not in item.keys():
                    param = f"{param}="
                    original_url = item["originalURL"]
                    param_value = None
                    with contextlib.suppress(IndexError):
                        # Extracting parameter value from original URL
                        # i.e "talent" from http://airbyte.io/?utm_source=talent
                        param_value = original_url.split(param, 2)[1].split("&", 1)[0]
                    item[resp_field] = param_value
            yield item


# Clicks stream
class Clicks(HttpStream, ABC):
    """
    This stream attempts to return the list of raw clicks from shortio.
    """

    url_base = "https://api-v2.short.cm/statistics/domain/"
    before_dt = datetime.datetime.now().__str__()
    domain_id = None
    start_date = None

    @property
    def http_method(self) -> str:
        return "POST"

    @property
    def cursor_field(self) -> str:
        """
        :return str: The name of the cursor field.
        """
        return "dt"

    @property
    def primary_key(self) -> Optional[Any]:
        return None

    @property
    def limit(self) -> int:
        return 1000

    state_checkpoint_interval = limit

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        # Get all the links
        return f"{self.domain_id}/last_clicks"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This function goes through the API responses and ensures that no more requests are left to take place
        :return str: min(dt) object from the previous API response.
        """
        clicks = json.loads(response.text)
        try:
            before_dt = sorted(clicks, key=lambda k: k["dt"], reverse=False)[0]["dt"]
            return None if self.limit > len(clicks) else before_dt
        except IndexError:
            return None

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, any]:
        """
        Here we keep track of the state between different syncs to ensure that the data fetched is correct.
        When the object is created, the datetime is taken and records are fetched until that point.
        Due to varying duration possibilities this allows to a reproducable set of results"
        """
        # This method is called once for each record returned from the API to compare the cursor field value in that record with the current state
        # we then return an updated state object. If this is the first time we run a sync or no state was passed, current_stream_state will be None.
        if current_stream_state is not None and "dt" in current_stream_state:
            return {"dt": self.before_dt}
        else:
            return {"dt": self.start_date}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        This method passes the arguments necessary to get the clicks from the shortio API.
        No parameters have been implemented here at all with the exception of hardcoding human clicks only to come through.
        Human clicks are hardcoded to reduce unnecessary clicks from coming through. Some resources from short.io:
        https://help.short.io/en/articles/4065954-how-short-io-tracks-clicks
        https://help.short.io/en/articles/4890644-what-are-the-redirects

        :return dict: json body for the request
        """
        return {
            "limit": self.limit,
            "include": {"human": True},
            "beforeDate": next_page_token or self.before_dt,
            "afterDate": stream_state["dt"] if stream_state and "dt" in stream_state.keys() else self.start_date,
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from json.loads(response.text)


# Source
class SourceShortio(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        CHeck whether configuration is correct.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:

            url = "https://api.short.io/api/domains"
            api_secret = config["secret_key"]
            domain_id = int(config["domain_id"])
            headers = {"Accept": "application/json", "Authorization": api_secret}

            response = requests.request("GET", url, headers=headers)
            response.raise_for_status()
            for domain in response.json():
                if domain_id == domain["id"]:
                    return True, None
        except Exception as e:
            return False, e

        return False, "Domain not found"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        key = config["secret_key"]
        auth = BasicAuthenticator(token=key, auth_method=None)
        links = Links(authenticator=auth)
        links.domain_id = config["domain_id"]
        clicks = Clicks(authenticator=auth)
        clicks.domain_id = config["domain_id"]
        clicks.start_date = config["start_date"]
        return [clicks, links]
