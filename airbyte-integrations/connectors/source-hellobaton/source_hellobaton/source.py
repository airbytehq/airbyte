#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources.streams import Stream

from .streams import (
    HellobatonStream,
    Companies,
    Milestones,
    Projects,
    Phases,
    ProjectAttachments,
    Tasks,
    TaskAttachments,
    Templates,
    TimeEntries,
    Users
)

STREAMS = [
    Companies,
    Milestones,
    Projects,
    Phases,
    ProjectAttachments,
    Tasks,
    TaskAttachments,
    Templates,
    TimeEntries,
    Users
]

#TODO ADD INCREMENTAL STATE
# # Basic incremental stream
# class IncrementalHellobatonStream(HellobatonStream, ABC):
#     """
#     TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
#          if you do not need to implement incremental sync for any streams, remove this class.
#     """

#     # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
#     state_checkpoint_interval = None

#     @property
#     def cursor_field(self) -> str:
#         """
#         TODO
#         Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
#         usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

#         :return str: The name of the cursor field.
#         """
#         return []

#     def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
#         """
#         Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
#         the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
#         """
#         return {}


# Source
class SourceHellobaton(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, any]) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        url_template="https://{company}.hellobaton.com/api/"
        try:
            params = {
                "api_key": config["api_key"],
                }
            base_url = url_template.format(company=config["company"])
            #This is just going to return a mapping of available endpoints
            response = requests.get(base_url, params=params)
            status_code = response.status_code
            logger.info(f"Status code: {status_code}")
            if status_code == 200:
                return True, None

        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [stream(company=config["company"], api_key=config["api_key"]) for stream in STREAMS]
