#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Optional

from airbyte_cdk import TState
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from source_klaviyo.streams import CampaignsEmail, CampaignsSMS, CampaignsEmailDetailed, CampaignsSMSDetailed, Flows


class SourceKlaviyo(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

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
                CampaignsEmail(api_key=api_key, start_date=start_date),
                CampaignsSMS(api_key=api_key, start_date=start_date),
                CampaignsEmailDetailed(api_key=api_key, start_date=start_date),
                CampaignsSMSDetailed(api_key=api_key, start_date=start_date),
                Flows(api_key=api_key, start_date=start_date),
            ]
        )
        return streams
