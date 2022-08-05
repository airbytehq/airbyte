#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from base64 import b64encode
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator


class QualarooStream(HttpStream, ABC):
    url_base = "https://api.qualaroo.com/api/v1/"

    # Define primary key as sort key for full_refresh, or very first sync for incremental_refresh
    primary_key = "id"

    # Page size
    limit = 500

    extra_params = None

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=config["authenticator"])
        self.start_date = config["start_date"]
        self.config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.limit, "start_date": self.start_date}
        if next_page_token:
            params.update(**next_page_token)
        if self.extra_params:
            params.update(self.extra_params)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        for record in json_response:
            yield record


class ChildStreamMixin:
    parent_stream_class: Optional[QualarooStream] = None

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for item in self.parent_stream_class(config=self.config).read_records(sync_mode=sync_mode):
            yield {"id": item["id"]}


class Surveys(QualarooStream):
    """Return list of all Surveys.
    API Docs: https://help.qualaroo.com/hc/en-us/articles/201969438-The-REST-Reporting-API
    Endpoint: https://api.qualaroo.com/api/v1/nudges/
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "nudges"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        survey_ids = self.config.get("survey_ids", [])
        for record in super().parse_response(response, **kwargs):
            if not survey_ids or record["id"] in survey_ids:
                yield record


class Responses(ChildStreamMixin, QualarooStream):
    """Return list of all responses of a survey.
    API Docs: hhttps://help.qualaroo.com/hc/en-us/articles/201969438-The-REST-Reporting-API
    Endpoint: https://api.qualaroo.com/api/v1/nudges/<id>/responses.json
    """

    parent_stream_class = Surveys
    limit = 500
    extra_params = {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json()

        # de-nest the answered_questions object if exists
        for rec in response_data:
            if "answered_questions" in rec:
                rec["answered_questions"] = list(rec["answered_questions"].values())
        yield from response_data

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"nudges/{stream_slice['id']}/responses.json"


class QualarooAuthenticator(HttpAuthenticator):
    """
    Generate auth header for start making requests from API token and API key.
    """

    def __init__(
        self,
        key: str,
        token: str,
        auth_header: str = "Authorization",
        key_header: str = "oauth_consumer_key",
        token_header: str = "oauth_token",
    ):
        self._key = key
        self._token = token
        self._token = b64encode(b":".join((key.encode("latin1"), token.encode("latin1")))).strip().decode("ascii")
        self.auth_header = auth_header
        self.key_header = key_header
        self.token_header = token_header

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"Basic {self._token}"}


class SourceQualaroo(AbstractSource):
    """
    Source Qualaroo fetch date from web-based, Kanban-style, list-making application.
    """

    @staticmethod
    def _get_authenticator(config: dict) -> QualarooAuthenticator:
        key, token = config["key"], config["token"]
        return QualarooAuthenticator(token=token, key=key)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector by granting the credentials.
        """

        try:
            url = f"{QualarooStream.url_base}nudges"

            authenticator = self._get_authenticator(config)

            response = requests.get(url, headers=authenticator.get_auth_header())

            response.raise_for_status()
            available_surveys = {row.get("id") for row in response.json()}
            for survey_id in config.get("survey_ids", []):
                if survey_id not in available_surveys:
                    return False, f"survey_id {survey_id} not found"
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config["authenticator"] = self._get_authenticator(config)
        return [Surveys(config), Responses(config)]
