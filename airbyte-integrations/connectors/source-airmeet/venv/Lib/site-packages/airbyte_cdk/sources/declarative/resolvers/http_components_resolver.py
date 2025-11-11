#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping

import dpath
from typing_extensions import deprecated

from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.resolvers.components_resolver import (
    ComponentMappingDefinition,
    ComponentsResolver,
    ResolvedComponentMappingDefinition,
)
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.source import ExperimentalClassWarning
from airbyte_cdk.sources.streams.concurrent.partitions.stream_slicer import StreamSlicer
from airbyte_cdk.sources.types import Config


@deprecated("This class is experimental. Use at your own risk.", category=ExperimentalClassWarning)
@dataclass
class HttpComponentsResolver(ComponentsResolver):
    """
    Resolves and populates stream templates with components fetched via an HTTP retriever.

    Attributes:
        retriever (Retriever): The retriever used to fetch data from an API.
        stream_slicer (StreamSlicer): The how the data is sliced.
        config (Config): Configuration object for the resolver.
        components_mapping (List[ComponentMappingDefinition]): List of mappings to resolve.
        parameters (InitVar[Mapping[str, Any]]): Additional parameters for interpolation.
    """

    retriever: Retriever
    stream_slicer: StreamSlicer
    config: Config
    components_mapping: List[ComponentMappingDefinition]
    parameters: InitVar[Mapping[str, Any]]
    _resolved_components: List[ResolvedComponentMappingDefinition] = field(
        init=False, repr=False, default_factory=list
    )

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        """
        Initializes and parses component mappings, converting them to resolved definitions.

        Args:
            parameters (Mapping[str, Any]): Parameters for interpolation.
        """
        for component_mapping in self.components_mapping:
            if isinstance(component_mapping.value, (str, InterpolatedString)):
                interpolated_value = (
                    InterpolatedString.create(component_mapping.value, parameters=parameters)
                    if isinstance(component_mapping.value, str)
                    else component_mapping.value
                )

                field_path = [
                    InterpolatedString.create(path, parameters=parameters)
                    for path in component_mapping.field_path
                ]

                self._resolved_components.append(
                    ResolvedComponentMappingDefinition(
                        field_path=field_path,
                        value=interpolated_value,
                        value_type=component_mapping.value_type,
                        parameters=parameters,
                    )
                )
            else:
                raise ValueError(
                    f"Expected a string or InterpolatedString for value in mapping: {component_mapping}"
                )

    def resolve_components(
        self, stream_template_config: Dict[str, Any]
    ) -> Iterable[Dict[str, Any]]:
        """
        Resolves components in the stream template configuration by populating values.

        Args:
            stream_template_config (Dict[str, Any]): Stream template to populate.

        Yields:
            Dict[str, Any]: Updated configurations with resolved components.
        """
        kwargs = {"stream_template_config": stream_template_config}

        for stream_slice in self.stream_slicer.stream_slices():
            for components_values in self.retriever.read_records(
                records_schema={}, stream_slice=stream_slice
            ):
                updated_config = deepcopy(stream_template_config)
                kwargs["components_values"] = components_values  # type: ignore[assignment] # component_values will always be of type Mapping[str, Any]
                kwargs["stream_slice"] = stream_slice  # type: ignore[assignment] # stream_slice will always be of type Mapping[str, Any]

                for resolved_component in self._resolved_components:
                    valid_types = (
                        (resolved_component.value_type,) if resolved_component.value_type else None
                    )
                    value = resolved_component.value.eval(
                        self.config, valid_types=valid_types, **kwargs
                    )

                    path = [
                        path.eval(self.config, **kwargs) for path in resolved_component.field_path
                    ]
                    dpath.set(updated_config, path, value)

                yield updated_config
