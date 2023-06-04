#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, List, Mapping, Optional, Tuple
from urllib.parse import urlparse

import jsonschema
import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from source_google_search_console.exceptions import InvalidSiteURLValidationError
from source_google_search_console.service_account_authenticator import ServiceAccountAuthenticator
from source_google_search_console.streams import (
    SearchAnalyticsAllFields,
    SearchAnalyticsByCountry,
    SearchAnalyticsByCustomDimensions,
    SearchAnalyticsByDate,
    SearchAnalyticsByDevice,
    SearchAnalyticsByPage,
    SearchAnalyticsByQuery,
    Sitemaps,
    Sites,
)

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


class SourceGoogleSearchConsole(AbstractSource):
    @staticmethod
    def normalize_url(url):
        parse_result = urlparse(url)
        if parse_result.path == "":
            parse_result = parse_result._replace(path="/")
        return parse_result.geturl()

    def _validate_and_transform(self, config: Mapping[str, Any]):
        authorization = config["authorization"]
        if authorization["auth_type"] == "Service":
            try:
                authorization["service_account_info"] = json.loads(authorization["service_account_info"])
            except ValueError:
                raise Exception("authorization.service_account_info is not valid JSON")

        if "custom_reports" in config:
            try:
                config["custom_reports"] = json.loads(config["custom_reports"])
            except ValueError:
                raise Exception("custom_reports is not valid JSON")
            jsonschema.validate(config["custom_reports"], custom_reports_schema)
            for report in config["custom_reports"]:
                for dimension in report["dimensions"]:
                    if dimension not in SearchAnalyticsByCustomDimensions.dimension_to_property_schema_map:
                        raise Exception(f"dimension: '{dimension}' not found")

        pendulum.parse(config["start_date"])
        end_date = config.get("end_date")
        if end_date:
            pendulum.parse(end_date)
        config["end_date"] = end_date or pendulum.now().to_date_string()

        config["site_urls"] = [self.normalize_url(url) for url in config["site_urls"]]

        config["data_state"] = config.get("date_state", "final")
        return config

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            config = self._validate_and_transform(config)
            stream_kwargs = self.get_stream_kwargs(config)
            self.validate_site_urls(config["site_urls"], stream_kwargs["authenticator"])
            sites = Sites(**stream_kwargs)
            stream_slice = sites.stream_slices(SyncMode.full_refresh)

            # stream_slice returns all site_urls and we need to make sure that
            # the connection is successful for all of them
            for _slice in stream_slice:
                sites_gen = sites.read_records(sync_mode=SyncMode.full_refresh, stream_slice=_slice)
                next(sites_gen)
            return True, None

        except (InvalidSiteURLValidationError, jsonschema.ValidationError) as e:
            return False, repr(e)
        except Exception as error:
            return (
                False,
                f"Unable to connect to Google Search Console API with the provided credentials - {repr(error)}",
            )

    @staticmethod
    def validate_site_urls(site_urls, auth):
        if isinstance(auth, ServiceAccountAuthenticator):
            request = auth(requests.Request(method="GET", url="https://www.googleapis.com/webmasters/v3/sites"))
            with requests.Session() as s:
                response = s.send(s.prepare_request(request))
        else:
            response = requests.get("https://www.googleapis.com/webmasters/v3/sites", headers=auth.get_auth_header())
        response_data = response.json()

        if response.status_code != 200:
            raise Exception(f"Unable to connect to Google Search Console API - {response_data}")

        remote_site_urls = {s["siteUrl"] for s in response_data["siteEntry"]}
        invalid_site_url = set(site_urls) - remote_site_urls
        if invalid_site_url:
            raise InvalidSiteURLValidationError(f'The following URLs are not permitted: {", ".join(invalid_site_url)}')

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = self._validate_and_transform(config)
        stream_config = self.get_stream_kwargs(config)

        streams = [
            Sites(**stream_config),
            Sitemaps(**stream_config),
            SearchAnalyticsByCountry(**stream_config),
            SearchAnalyticsByDevice(**stream_config),
            SearchAnalyticsByDate(**stream_config),
            SearchAnalyticsByQuery(**stream_config),
            SearchAnalyticsByPage(**stream_config),
            SearchAnalyticsAllFields(**stream_config),
        ]

        streams = streams + self.get_custom_reports(config=config, stream_config=stream_config)

        return streams

    def get_custom_reports(self, config: Mapping[str, Any], stream_config: Mapping[str, Any]) -> List[Optional[Stream]]:
        return [
            type(report["name"], (SearchAnalyticsByCustomDimensions,), {})(dimensions=report["dimensions"], **stream_config)
            for report in config.get("custom_reports", [])
        ]

    def get_stream_kwargs(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "site_urls": config["site_urls"],
            "start_date": config["start_date"],
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
