#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import (
    Activity,
    Companies,
    Milestones,
    Phases,
    ProjectAttachments,
    Projects,
    TaskAttachments,
    Tasks,
    Templates,
    TimeEntries,
    Users,
)

STREAMS = [Activity, Companies, Milestones, Projects, Phases, ProjectAttachments, Tasks, TaskAttachments, Templates, TimeEntries, Users]


# Source
class SourceHellobaton(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, any]) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        url_template = "https://{company}.hellobaton.com/api/"
        try:
            params = {
                "api_key": config["api_key"],
            }
            base_url = url_template.format(company=config["company"])
            # This is just going to return a mapping of available endpoints
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
