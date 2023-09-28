#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import re
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream

stream_json_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "_id": {
            "type": [
                "number",
                "null",
            ]
        },
        "endtime": {"type": ["string", "null"]},
    },
}


class KoboToolStream(HttpStream, IncrementalMixin):
    """
    submission_date_format = "%Y-%m-%dT%H:%M:%S"
    end_time_format = "%Y-%m-%dT%H:%M:%S.%.3f%z"
    """

    primary_key = "_id"
    cursor_field = "endtime"

    def __init__(self, config: Mapping[str, Any], form_id, schema, name, pagination_limit, auth_token, **kwargs):
        super().__init__()
        self.form_id = form_id
        self.auth_token = auth_token
        self.schema = schema
        self.stream_name = name
        self.base_url = config["base_url"]
        self.PAGINATION_LIMIT = pagination_limit
        self._cursor_value = None
        self.start_time = config["start_time"]
        self.exclude_fields = config["exclude_fields"] if "exclude_fields" in config else []

    @property
    def url_base(self) -> str:
        return f"{self.base_url}/api/v2/assets/{self.form_id}/"

    @property
    def name(self) -> str:
        # Return the english substring as stream name. If not found return form uid
        regex = re.compile("[^a-zA-Z ]")
        s = regex.sub("", self.stream_name)
        s = s.strip()
        return s if len(s) > 0 else self.form_id

    # State will be a dict : {'endtime': '2023-03-15T00:00:00.000+05:30'}

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self.start_time}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def get_json_schema(self):
        return self.schema

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"start": 0, "limit": self.PAGINATION_LIMIT, "sort": json.dumps({self.cursor_field: 1})}
        params["query"] = json.dumps({self.cursor_field: {"$gte": self.state[self.cursor_field]}})

        if next_page_token:
            params.update(next_page_token)

        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response: Mapping[str, str] = response.json()
        next_url = json_response.get("next")
        params = None
        if next_url is not None:
            parsed_url = urlparse(next_url)
            params = dict(parse_qsl(parsed_url.query))
        return params

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "data.json"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Authorization": "Token " + self.auth_token}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        result = json_response.get("results")

        for record in result:
            for to_remove_field in self.exclude_fields:
                if to_remove_field in record:
                    record.pop(to_remove_field)
            yield record

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            self._cursor_value = record[self.cursor_field]
            yield record


class SourceKobotoolbox(AbstractSource):
    # API_URL = "https://kf.kobotoolbox.org/api/v2"
    # TOKEN_URL = "https://kf.kobotoolbox.org/token/?format=json"
    PAGINATION_LIMIT = 30000

    @classmethod
    def _check_credentials(cls, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        # check if the credentials are provided correctly, because for now these value are not required in spec
        if not config.get("username"):
            return False, "username in credentials is not provided"

        if not config.get("password"):
            return False, "password in credentials is not provided"

        return True, None

    def get_access_token(self, config) -> Tuple[str, any]:
        token_url = f"{config['base_url']}/token/?format=json"

        try:
            response = requests.post(token_url, auth=(config["username"], config["password"]))
            response.raise_for_status()
            json_response = response.json()
            return (json_response.get("token", None), None) if json_response is not None else (None, None)
        except requests.exceptions.RequestException as e:
            return None, e

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        is_valid_credentials, msg = self._check_credentials(config)
        if not is_valid_credentials:
            return is_valid_credentials, msg

        url = f"{config['base_url']}/api/v2/assets.json"
        response = requests.get(url, auth=(config["username"], config["password"]))

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return False, "Something went wrong. Please check your credentials"

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # Fetch all assets(forms)
        url = f"{config['base_url']}/api/v2/assets.json"
        response = requests.get(url, auth=(config["username"], config["password"]))
        json_response = response.json()
        key_list = json_response.get("results")

        # Generate a auth token for all streams
        auth_token, msg = self.get_access_token(config)
        if auth_token is None:
            return []

        # Generate array of stream objects
        streams = []
        for form_dict in key_list:
            if form_dict["has_deployment"]:
                stream = KoboToolStream(
                    config=config,
                    form_id=form_dict["uid"],
                    schema=stream_json_schema,
                    name=form_dict["name"],
                    pagination_limit=self.PAGINATION_LIMIT,
                    auth_token=auth_token,
                )
                streams.append(stream)

        return streams
