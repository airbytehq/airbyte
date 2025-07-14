#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import hvac
from airbyte_cdk.sources.streams import Stream


class VaultStream(Stream, ABC):
    """Base stream class for HashiCorp Vault."""
    
    def __init__(self, client: hvac.Client, config: Mapping[str, Any], namespace: str = "", **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.config = config
        self.namespace = namespace
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stream name."""
        pass
    
    @property
    def primary_key(self) -> Optional[str]:
        """Return the primary key field."""
        return "id"
    
    def get_json_schema(self) -> Mapping[str, Any]:
        """Return the json schema for the stream."""
        # Override in each stream with specific schema
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {}
        }
        
    def read_records(
        self,
        sync_mode,
        cursor_field: Optional[str] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read records from the stream."""
        # This will be implemented by each specific stream
        yield from []