#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .auth import DiscourseAuthenticator
from .streams import LatestTopics, Posts, TagGroups


# Source
class SourceDiscourse(AbstractSource):
    @staticmethod
    def get_authenticator(config):
        api_key = config.get("api_key", None)
        api_username = config.get("api_username", None)
        if not api_key:
            raise Exception("Config validation error: 'api_key' is a required property")
        elif not api_username:
            raise Exception("Config validation error: 'api_username' is a required property")
        auth = DiscourseAuthenticator(config["api_key"], config["api_username"])
        return auth

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        auth = self.get_authenticator(config)
        try:
            tags_stream = TagGroups(authenticator=auth)
            tags_records = tags_stream.read_records(sync_mode="full_refresh")
            record = next(tags_records)
            logger.info(f"Successfully connected to the Tags stream. Pulled one record: {record}")
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_authenticator(config)
        return [TagGroups(authenticator=auth), LatestTopics(authenticator=auth), Posts(authenticator=auth)]
