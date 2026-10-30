#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import InitVar, dataclass
from http import HTTPStatus
from typing import Any, Mapping, MutableMapping, Optional, Union

import dpath.util
import pendulum
import requests
from requests import HTTPError

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy


@dataclass
class AuthenticatorFacebookPageAccessToken(NoAuth):
    config: Config
    page_id: Union[InterpolatedString, str]
    access_token: Union[InterpolatedString, str]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._page_id = InterpolatedString.create(self.page_id, parameters=parameters).eval(self.config)
        self._access_token = InterpolatedString.create(self.access_token, parameters=parameters).eval(self.config)

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the page access token to params to authenticate on the HTTP request"""
        page_access_token = self.generate_page_access_token()
        request.prepare_url(url=request.url, params={"access_token": page_access_token})
        return request

    def generate_page_access_token(self) -> str:
        # We are expecting to receive User access token from config. To access
        # Pages API we need to generate Page access token. Page access tokens
        # can be generated from another Page access token (with the same page ID)
        # so if user manually set Page access token instead of User access
        # token it would be no problem unless it has wrong page ID.
        # https://developers.facebook.com/docs/pages/access-tokens#get-a-page-access-token
        try:
            r = requests.get(
                f"https://graph.facebook.com/{self._page_id}", params={"fields": "access_token", "access_token": self._access_token}
            )
            if r.status_code != HTTPStatus.OK:
                raise HTTPError(r.text)
            return r.json().get("access_token")
        except Exception as e:
            raise Exception(f"Error while generating page access token: {e}") from e


@dataclass
class CustomFieldTransformation(RecordTransformation):
    """
    Transform all 'date-time' fields from schema (nested included) to rfc3339 format
    Issue: https://github.com/airbytehq/airbyte/issues/23407
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.name = parameters.get("name")

    def _get_schema_root_properties(self):
        schema_loader = JsonFileSchemaLoader(config=self.config, parameters={"name": self.name})
        schema = schema_loader.get_json_schema()
        return schema["properties"]

    def _get_date_time_dpath_from_schema(self):
        """
        Get all dpath in format 'a/b/*/c' from schema with format: 'date-time'
        """
        schema = self._get_schema_root_properties()
        all_results = dpath.util.search(schema, "**", yielded=True, afilter=lambda x: True if "date-time" in str(x) else False)
        full_dpath = [x[0] for x in all_results if isinstance(x[1], dict) and x[1].get("format") == "date-time"]
        return [path.replace("/properties", "").replace("items", "*") for path in full_dpath]

    def _date_time_to_rfc3339(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Transform 'date-time' items to RFC3339 format
        """
        date_time_paths = self._get_date_time_dpath_from_schema()
        for path in date_time_paths:
            if "*" not in path:
                if field_value := dpath.util.get(record, path, default=None):
                    dpath.util.set(record, path, pendulum.parse(field_value).to_rfc3339_string())
            else:
                if field_values := dpath.util.values(record, path):
                    for i, date_time_value in enumerate(field_values):
                        dpath.util.set(record, path.replace("*", str(i)), pendulum.parse(date_time_value).to_rfc3339_string())
        return record

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        return self._date_time_to_rfc3339(record)


@dataclass
class MetaUsageBackoffStrategy(BackoffStrategy):
    """
    When Meta throttles a request it reports how long until access returns in the
    X-Business-Use-Case-Usage header (`estimated_time_to_regain_access`, in minutes).
    Wait that long instead of guessing with exponential backoff; return None when the
    header is absent so the next strategy in the list decides.
    https://developers.facebook.com/docs/graph-api/overview/rate-limiting/
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    # ponytail: cap at 30 minutes; Meta can estimate hours and a sync should fail fast past that.
    max_wait_seconds: int = 1800

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        pass

    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int,
    ) -> Optional[float]:
        if not isinstance(response_or_exception, requests.Response):
            return None
        try:
            usage = json.loads(response_or_exception.headers.get("X-Business-Use-Case-Usage", ""))
        except ValueError:
            return None
        minutes = max(
            (entry.get("estimated_time_to_regain_access", 0) for entries in usage.values() for entry in entries),
            default=0,
        )
        return min(minutes * 60, self.max_wait_seconds) if minutes > 0 else None
