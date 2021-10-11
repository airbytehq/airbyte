#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_pipedrive.streams import Activities, ActivityFields, Deals, Leads, Organizations, Persons, Pipelines, Stages, Users


class SourcePipedrive(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            deals = Deals(api_token=config["api_token"], replication_start_date=pendulum.parse(config["replication_start_date"]))
            deals_gen = deals.read_records(sync_mode=SyncMode.full_refresh)
            next(deals_gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Pipedrive API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        stream_kwargs = {"api_token": config["api_token"]}
        incremental_stream_kwargs = {**stream_kwargs, "replication_start_date": pendulum.parse(config["replication_start_date"])}
        streams = [
            Activities(**incremental_stream_kwargs),
            ActivityFields(**stream_kwargs),
            Deals(**incremental_stream_kwargs),
            Leads(**stream_kwargs),
            Organizations(**incremental_stream_kwargs),
            Persons(**incremental_stream_kwargs),
            Pipelines(**incremental_stream_kwargs),
            Stages(**incremental_stream_kwargs),
            Users(**incremental_stream_kwargs),
        ]
        return streams
