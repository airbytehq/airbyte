#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from source_google_search_console.service_account_authenticator import ServiceAccountAuthenticator
from source_google_search_console.streams import (
    SearchAnalyticsAllFields,
    SearchAnalyticsByCountry,
    SearchAnalyticsByDate,
    SearchAnalyticsByDevice,
    SearchAnalyticsByPage,
    SearchAnalyticsByQuery,
    Sitemaps,
    Sites,
)


class SourceGoogleSearchConsole(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            stream_kwargs = self.get_stream_kwargs(config)
            sites = Sites(**stream_kwargs)
            stream_slice = sites.stream_slices(SyncMode.full_refresh)

            # stream_slice returns all site_urls and we need to make sure that
            # the connection is successful for all of them
            for _slice in stream_slice:
                sites_gen = sites.read_records(sync_mode=SyncMode.full_refresh, stream_slice=_slice)
                next(sites_gen)
            return True, None

        except Exception as error:
            return (
                False,
                f"Unable to connect to Google Search Console API with the provided credentials - {repr(error)}",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

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

        return streams

    @staticmethod
    def get_stream_kwargs(config: Mapping[str, Any]) -> Mapping[str, Any]:
        authorization = config.get("authorization", {})

        stream_kwargs = {
            "site_urls": config.get("site_urls"),
            "start_date": config.get("start_date"),
            "end_date": config.get("end_date") or pendulum.now().to_date_string(),
        }

        auth_type = authorization.get("auth_type")
        if auth_type == "Client":
            stream_kwargs["authenticator"] = Oauth2Authenticator(
                token_refresh_endpoint="https://oauth2.googleapis.com/token",
                client_secret=authorization.get("client_secret"),
                client_id=authorization.get("client_id"),
                refresh_token=authorization.get("refresh_token"),
            )
        elif auth_type == "Service":
            stream_kwargs["authenticator"] = ServiceAccountAuthenticator(
                service_account_info=json.loads(authorization.get("service_account_info")), email=authorization.get("email")
            )
        else:
            raise Exception(f"Invalid auth type: {auth_type}")

        return stream_kwargs
