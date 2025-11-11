#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping

import dpath
import yaml
from typing_extensions import deprecated
from yaml.parser import ParserError

from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.resolvers.components_resolver import (
    ComponentMappingDefinition,
    ComponentsResolver,
    ResolvedComponentMappingDefinition,
)
from airbyte_cdk.sources.source import ExperimentalClassWarning
from airbyte_cdk.sources.types import Config


@deprecated("This class is experimental. Use at your own risk.", category=ExperimentalClassWarning)
@dataclass
class StreamParametersDefinition:
    """
    Represents a stream parameters definition to set up dynamic streams from defined values in manifest.
    """

    list_of_parameters_for_stream: List[Dict[str, Any]]


@deprecated("This class is experimental. Use at your own risk.", category=ExperimentalClassWarning)
@dataclass
class ParametrizedComponentsResolver(ComponentsResolver):
    """
    Resolves and populates dynamic streams from defined parametrized values in manifest.
    """

    stream_parameters: StreamParametersDefinition
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
                        create_or_update=component_mapping.create_or_update,
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
        kwargs = {"stream_template_config": stream_template_config}

        for components_values in self.stream_parameters.list_of_parameters_for_stream:
            updated_config = deepcopy(stream_template_config)
            kwargs["components_values"] = components_values  # type: ignore[assignment] # component_values will always be of type Mapping[str, Any]
            for resolved_component in self._resolved_components:
                valid_types = (
                    (resolved_component.value_type,) if resolved_component.value_type else None
                )
                value = resolved_component.value.eval(
                    self.config, valid_types=valid_types, **kwargs
                )
                path = [path.eval(self.config, **kwargs) for path in resolved_component.field_path]
                parsed_value = self._parse_yaml_if_possible(value)
                # https://github.com/dpath-maintainers/dpath-python/blob/master/dpath/__init__.py#L136
                # dpath.set returns the number of changed elements, 0 when no elements changed
                updated = dpath.set(updated_config, path, parsed_value)

                if parsed_value and not updated and resolved_component.create_or_update:
                    dpath.new(updated_config, path, parsed_value)

            yield updated_config

    @staticmethod
    def _parse_yaml_if_possible(value: Any) -> Any:
        """
        Try to turn value into a Python object by YAML-parsing it.

        * If value is a `str` and can be parsed by `yaml.safe_load`,
          return the parsed result.
        * If parsing fails (`yaml.parser.ParserError`) – or value is not
          a string at all – return the original value unchanged.
        """
        if isinstance(value, str):
            try:
                return yaml.safe_load(value)
            except ParserError:  # "{{ record[0] in ['cohortActiveUsers'] }}"   # not valid YAML
                return value
        return value
