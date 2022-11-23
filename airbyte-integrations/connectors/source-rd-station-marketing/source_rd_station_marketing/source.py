#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from source_rd_station_marketing.streams import (
    AnalyticsConversions,
    AnalyticsEmails,
    AnalyticsFunnel,
    AnalyticsWorkflowEmailsStatistics,
    Emails,
    Embeddables,
    Fields,
    LandingPages,
    Popups,
    Segmentations,
    Workflows,
)


class SourceRDStationMarketing(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            stream_kwargs = self.get_stream_kwargs(config)
            segmentations = Segmentations(**stream_kwargs)
            segmentations_gen = segmentations.read_records(sync_mode=SyncMode.full_refresh)
            next(segmentations_gen)
            return True, None
        except Exception as error:
            return (
                False,
                f"Unable to connect to RD Station Marketing API with the provided credentials - {repr(error)}",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        stream_kwargs = self.get_stream_kwargs(config)
        incremental_kwargs = {**stream_kwargs, "start_date": pendulum.parse(config["start_date"])}
        streams = [
            AnalyticsEmails(**incremental_kwargs),
            AnalyticsConversions(**incremental_kwargs),
            AnalyticsFunnel(**incremental_kwargs),
            AnalyticsWorkflowEmailsStatistics(**incremental_kwargs),
            Emails(**stream_kwargs),
            Embeddables(**stream_kwargs),
            Fields(**stream_kwargs),
            LandingPages(**stream_kwargs),
            Popups(**stream_kwargs),
            Segmentations(**stream_kwargs),
            Workflows(**stream_kwargs),
        ]
        return streams

    @staticmethod
    def get_stream_kwargs(config: Mapping[str, Any]) -> Mapping[str, Any]:
        authorization = config.get("authorization", {})
        stream_kwargs = dict()

        stream_kwargs["authenticator"] = Oauth2Authenticator(
            token_refresh_endpoint="https://api.rd.services/auth/token",
            client_secret=authorization.get("client_secret"),
            client_id=authorization.get("client_id"),
            refresh_token=authorization.get("refresh_token"),
        )
        return stream_kwargs
