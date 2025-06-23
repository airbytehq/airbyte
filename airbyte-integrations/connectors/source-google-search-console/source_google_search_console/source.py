#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, List, Mapping, Optional, Union
from urllib.parse import urlparse

import jsonschema
import pendulum
import requests

from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from airbyte_cdk.utils import AirbyteTracedException
from source_google_search_console.exceptions import (
    InvalidSiteURLValidationError,
    UnauthorizedOauthError,
    UnidentifiedError,
)
from source_google_search_console.service_account_authenticator import ServiceAccountAuthenticator


DIMENSION_TO_PROPERTY_SCHEMA_MAP = {
    "country": [{"country": {"type": ["null", "string"]}}],
    "date": [{"date": {"type": ["null", "string"], "format": "date"}}],
    "device": [{"device": {"type": ["null", "string"]}}],
    "page": [{"page": {"type": ["null", "string"]}}],
    "query": [{"query": {"type": ["null", "string"]}}],
}

custom_reports_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "dimensions": {"type": "array", "items": {"type": "string", "minLength": 1}},
        },
        "required": ["name", "dimensions"],
    },
}


class SourceGoogleSearchConsole(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    @staticmethod
    def normalize_url(url):
        parse_result = urlparse(url)
        if parse_result.path == "":
            parse_result = parse_result._replace(path="/")
        return parse_result.geturl()

    def _validate_and_transform(self, config: Mapping[str, Any]):
        # authorization checks
        authorization = config["authorization"]
        if authorization["auth_type"] == "Service":
            try:
                json.loads(authorization["service_account_info"])
            except ValueError:
                message = "authorization.service_account_info is not valid JSON"
                raise AirbyteTracedException(message=message, internal_message=message, failure_type=FailureType.config_error)

        # custom report validation
        config = self._validate_custom_reports(config)

        # start date checks
        pendulum.parse(config.get("start_date", "2021-01-01"))  # `2021-01-01` is the default value

        # the `end_date` checks
        end_date = config.get("end_date")
        if end_date:
            pendulum.parse(end_date)
        config["end_date"] = end_date or pendulum.now().to_date_string()
        # site  urls checks
        config["site_urls"] = [self.normalize_url(url) for url in config["site_urls"]]
        # data state checks
        config["data_state"] = config.get("data_state", "final")
        return config

    def _validate_custom_reports(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        if "custom_reports_array" in config:
            try:
                custom_reports = config["custom_reports_array"]
                if isinstance(custom_reports, str):
                    # load the json_str old report structure and transform it into valid JSON Object
                    config["custom_reports_array"] = json.loads(config["custom_reports_array"])
                elif isinstance(custom_reports, list):
                    pass  # allow the list structure only
            except ValueError:
                message = "Custom Reports provided is not valid List of Object (reports)"
                raise AirbyteTracedException(message=message, internal_message=message, failure_type=FailureType.config_error)
            jsonschema.validate(config["custom_reports_array"], custom_reports_schema)
            for report in config["custom_reports_array"]:
                for dimension in report["dimensions"]:
                    if dimension not in DIMENSION_TO_PROPERTY_SCHEMA_MAP:
                        message = f"dimension: '{dimension}' not found"
                        raise AirbyteTracedException(message=message, internal_message=message, failure_type=FailureType.config_error)
        return config

    def validate_site_urls(self, site_urls: List[str], auth: Union[ServiceAccountAuthenticator, Oauth2Authenticator]):
        if isinstance(auth, ServiceAccountAuthenticator):
            request = auth(requests.Request(method="GET", url="https://www.googleapis.com/webmasters/v3/sites"))
            with requests.Session() as s:
                response = s.send(s.prepare_request(request))
                # the exceptions for `service account` are handled in `service_account_authenticator.py`
        else:
            # catch the error while refreshing the access token
            auth_header = self.get_client_auth_header(auth)
            if "error" in auth_header:
                if auth_header.get("code", 0) in [400, 401]:
                    raise UnauthorizedOauthError
            # validate site urls with provided authenticator
            response = requests.get("https://www.googleapis.com/webmasters/v3/sites", headers=auth_header)
        # validate the status of the response, if it was successfull
        if response.status_code != 200:
            raise UnidentifiedError(response.json())

        remote_site_urls = {s["siteUrl"] for s in response.json().get("siteEntry", [])}
        invalid_site_url = set(site_urls) - remote_site_urls
        if invalid_site_url:
            raise InvalidSiteURLValidationError(invalid_site_url)

    def get_client_auth_header(self, auth: Oauth2Authenticator) -> Mapping[str, Any]:
        try:
            return auth.get_auth_header()
        except requests.exceptions.HTTPError as e:
            return {
                "code": e.response.status_code,
                "error": e.response.json(),
            }

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = self._validate_and_transform(config)
        stream_config = self.get_stream_kwargs(config)

        return super().streams(config=config)

    def get_stream_kwargs(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "site_urls": config["site_urls"],
            "start_date": config.get("start_date", "2021-01-01"),  # `2021-01-01` is the default value
            "end_date": config["end_date"],
            "authenticator": self.get_authenticator(config),
            "data_state": config["data_state"],
        }

    def get_authenticator(self, config):
        authorization = config["authorization"]
        auth_type = authorization["auth_type"]

        if auth_type == "Client":
            return Oauth2Authenticator(
                token_refresh_endpoint="https://oauth2.googleapis.com/token",
                client_secret=authorization["client_secret"],
                client_id=authorization["client_id"],
                refresh_token=authorization["refresh_token"],
            )
        elif auth_type == "Service":
            return ServiceAccountAuthenticator(
                service_account_info=authorization["service_account_info"],
                email=authorization["email"],
            )
