#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from source_klaviyo.streams import Campaigns, CampaignsDetailed, Flows


class SourceKlaviyo(YamlDeclarativeSource):
    def __init__(self) -> None:
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Discovery method, returns available streams
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        api_key = config["api_key"]
        start_date = config.get("start_date")
        streams = super().streams(config)
        streams.extend(
            [
                Campaigns(api_key=api_key, start_date=start_date),
                CampaignsDetailed(api_key=api_key, start_date=start_date),
                Flows(api_key=api_key, start_date=start_date),
            ]
        )
        return streams

    def continue_sync_on_stream_failure(self) -> bool:
        return True
