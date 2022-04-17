#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import copy
import logging
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.deprecated.base_source import ConfiguredAirbyteStream
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config
from airbyte_cdk.utils.event_timing import create_timer
from requests import HTTPError
from source_freshdesk.api import API
from source_freshdesk.errors import FreshdeskError, FreshdeskNotFound, FreshdeskUnauthorized
from source_freshdesk.streams import Agents, Companies, Contacts, Groups, Roles, SatisfactionRatings, Skills, TimeEntries


class SourceFreshdesk(AbstractSource):

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        alive = True
        error_msg = None
        try:
            api = API(domain=config['domain'], api_key=config['api_key'])
            api.get("settings/helpdesk")
        except (FreshdeskUnauthorized, FreshdeskNotFound):
            alive = False
            error_msg = "Invalid credentials"
        except FreshdeskError as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            Agents(config=config),
            Companies(config=config),
            Contacts(config=config),
            Groups(config=config),
            Roles(config=config),
            Skills(config=config),
            TimeEntries(config=config),
            SatisfactionRatings(config=config)
        ]
