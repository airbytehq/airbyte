#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_klaviyo.streams import Campaigns, Events, Flows, GlobalExclusions, Lists, Metrics


class SourceKlaviyo(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            # we use metrics endpoint because it never returns an error
            _ = list(Metrics(api_key=config["api_key"]).read_records(sync_mode=SyncMode.full_refresh))
        except Exception as e:
            return False, repr(e)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Discovery method, returns available streams
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        api_key = config["api_key"]
        start_date = config["start_date"]
        return [
            Campaigns(api_key=api_key),
            Events(api_key=api_key, start_date=start_date),
            GlobalExclusions(api_key=api_key, start_date=start_date),
            Lists(api_key=api_key),
            Metrics(api_key=api_key),
            Flows(api_key=api_key, start_date=start_date),
        ]
