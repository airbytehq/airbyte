#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Mapping, Optional, Tuple

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState

from .auth import AirtableAuth
from .streams import AirtableBases, AirtableTables


class SourceAirtable(YamlDeclarativeSource):
    _auth: AirtableAuth = None

    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        auth = AirtableAuth(config)
        try:
            # try reading first table from each base, to check the connectivity,
            for base in AirtableBases(authenticator=auth).read_records(sync_mode=SyncMode.full_refresh):
                base_id = base.get("id")
                base_name = base.get("name")
                self.logger.info(f"Reading first table info for base: {base_name}")
                next(AirtableTables(base_id=base_id, authenticator=auth).read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, str(e)
