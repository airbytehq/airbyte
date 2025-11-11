# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, List, Mapping, Optional

import dpath

from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.retrievers import Retriever
from airbyte_cdk.sources.types import Config, StreamSlice


@dataclass
class PropertiesFromEndpoint:
    """
    Component that defines the behavior around how to dynamically retrieve a set of request properties from an
    API endpoint. The set retrieved can then be injected into the requests to extract records from an API source.
    """

    property_field_path: List[str]
    retriever: Retriever
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    _cached_properties: Optional[List[str]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._property_field_path = [
            InterpolatedString(string=property_field, parameters=parameters)
            for property_field in self.property_field_path
        ]

    def get_properties_from_endpoint(self) -> List[str]:
        if self._cached_properties is None:
            self._cached_properties = list(
                map(
                    self._get_property,  # type: ignore # SimpleRetriever and AsyncRetriever only returns Record. Should we change the return type of Retriever.read_records?
                    self.retriever.read_records(records_schema={}, stream_slice=None),
                )
            )
        return self._cached_properties

    def _get_property(self, property_obj: Mapping[str, Any]) -> str:
        path = [
            node.eval(self.config) if not isinstance(node, str) else node
            for node in self._property_field_path
        ]
        return str(dpath.get(property_obj, path, default=[]))  # type: ignore # extracted will be a MutableMapping, given input data structure
