#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterator, List, Mapping, MutableMapping, Tuple

from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream

from .components import MetabaseAuth

API_URL = "instance_api_url"
USERNAME = "username"
PASSWORD = "password"
SESSION_TOKEN = "session_token"


class SourceMetabase(YamlDeclarativeSource):
    def __init__(self):
        self.session = None
        super().__init__(**{"path_to_yaml": "metabase.yaml"})

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        session = None
        try:
            session = MetabaseAuth(config, {})
            return session.has_valid_token(), None
        except Exception as e:
            return False, e
        finally:
            if session:
                session.close_session()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        self.session = MetabaseAuth(config, {})

        return super().streams(config)

    # We override the read method to make sure we close the metabase session and logout
    # so we don't keep too many active session_token active.
    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterator[AirbyteMessage]:
        try:
            yield from super().read(logger, config, catalog, state)
        finally:
            self.close_session()

    def close_session(self):
        if self.session:
            self.session.close_session()
