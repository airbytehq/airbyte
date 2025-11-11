# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional, Set, Union

from airbyte_cdk.models import ConfiguredAirbyteStream
from airbyte_cdk.sources.declarative.requesters.query_properties import (
    PropertiesFromEndpoint,
    PropertyChunking,
)
from airbyte_cdk.sources.declarative.requesters.query_properties.property_selector import (
    PropertySelector,
)
from airbyte_cdk.sources.types import Config, StreamSlice


@dataclass
class QueryProperties:
    """
    Low-code component that encompasses the behavior to inject additional property values into the outbound API
    requests. Property values can be defined statically within the manifest or dynamically by making requests
    to a partner API to retrieve the properties. Query properties also allow for splitting of the total set of
    properties into smaller chunks to satisfy API restrictions around the total amount of data retrieved
    """

    property_list: Optional[Union[List[str], PropertiesFromEndpoint]]
    always_include_properties: Optional[List[str]]
    property_chunking: Optional[PropertyChunking]
    property_selector: Optional[PropertySelector]
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def get_request_property_chunks(self) -> Iterable[List[str]]:
        """
        Uses the defined property_list to fetch the total set of properties dynamically or from a static list
        and based on the resulting properties, performs property chunking if applicable.
        """
        fields: List[str]
        configured_properties = self.property_selector.select() if self.property_selector else None

        if isinstance(self.property_list, PropertiesFromEndpoint):
            fields = self.property_list.get_properties_from_endpoint()
        else:
            fields = self.property_list if self.property_list else []

        if self.property_chunking:
            yield from self.property_chunking.get_request_property_chunks(
                property_fields=fields,
                always_include_properties=self.always_include_properties,
                configured_properties=configured_properties,
            )
        else:
            if configured_properties is not None:
                all_fields = (
                    [field for field in fields if field in configured_properties]
                    if configured_properties is not None
                    else list(fields)
                )
            else:
                all_fields = list(fields)

            if self.always_include_properties:
                all_fields = list(self.always_include_properties) + all_fields

            yield all_fields
