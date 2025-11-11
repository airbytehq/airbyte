#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from itertools import product
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union

import dpath
import yaml
from typing_extensions import deprecated
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.resolvers.components_resolver import (
    ComponentMappingDefinition,
    ComponentsResolver,
    ResolvedComponentMappingDefinition,
)
from airbyte_cdk.sources.source import ExperimentalClassWarning
from airbyte_cdk.sources.types import Config


@deprecated("This class is experimental. Use at your own risk.", category=ExperimentalClassWarning)
@dataclass
class StreamConfig:
    """
    Identifies stream config details for dynamic schema extraction and processing.
    """

    configs_pointer: List[Union[InterpolatedString, str]]
    parameters: InitVar[Mapping[str, Any]]
    default_values: Optional[List[Any]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.configs_pointer = [
            InterpolatedString.create(path, parameters=parameters) for path in self.configs_pointer
        ]


@deprecated("This class is experimental. Use at your own risk.", category=ExperimentalClassWarning)
@dataclass
class ConfigComponentsResolver(ComponentsResolver):
    """
    Resolves and populates stream templates with components fetched via source config.

    Attributes:
        stream_config (StreamConfig): The description of stream configuration used to fetch stream config from source config.
        config (Config): Configuration object for the resolver.
        components_mapping (List[ComponentMappingDefinition]): List of mappings to resolve.
        parameters (InitVar[Mapping[str, Any]]): Additional parameters for interpolation.
    """

    stream_configs: List[StreamConfig]
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
            interpolated_condition = (
                InterpolatedBoolean(condition=component_mapping.condition, parameters=parameters)
                if component_mapping.condition
                else None
            )

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
                        condition=interpolated_condition,
                    )
                )
            else:
                raise ValueError(
                    f"Expected a string or InterpolatedString for value in mapping: {component_mapping}"
                )

    @staticmethod
    def _merge_combination(combo: Iterable[Tuple[int, Any]]) -> Dict[str, Any]:
        """Collapse a combination of ``(idx, elem)`` into one config dict."""
        result: Dict[str, Any] = {}
        for config_index, (elem_index, elem) in enumerate(combo):
            if isinstance(elem, dict):
                result.update(elem)
            else:
                # keep non-dict values under an artificial name
                result.setdefault(f"source_config_{config_index}", (elem_index, elem))
        return result

    @property
    def _stream_config(self) -> List[Dict[str, Any]]:
        """
        Build every unique stream-configuration combination defined by
        each ``StreamConfig`` and any ``default_values``.
        """
        all_indexed_streams = []
        for stream_config in self.stream_configs:
            path = [
                node.eval(self.config) if not isinstance(node, str) else node
                for node in stream_config.configs_pointer
            ]
            stream_configs_raw = dpath.get(dict(self.config), path, default=[])
            stream_configs = (
                list(stream_configs_raw)
                if isinstance(stream_configs_raw, list)
                else [stream_configs_raw]
            )

            if stream_config.default_values:
                stream_configs.extend(stream_config.default_values)

            all_indexed_streams.append([(i, item) for i, item in enumerate(stream_configs)])
        return [
            self._merge_combination(combo)  # type: ignore[arg-type]
            for combo in product(*all_indexed_streams)
        ]

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

        for components_values in self._stream_config:
            updated_config = deepcopy(stream_template_config)
            kwargs["components_values"] = components_values  # type: ignore[assignment] # component_values will always be of type Mapping[str, Any]

            for resolved_component in self._resolved_components:
                if (
                    resolved_component.condition is not None
                    and not resolved_component.condition.eval(self.config, **kwargs)
                ):
                    continue

                valid_types = (
                    (resolved_component.value_type,) if resolved_component.value_type else None
                )
                value = resolved_component.value.eval(
                    self.config, valid_types=valid_types, **kwargs
                )

                path = [path.eval(self.config, **kwargs) for path in resolved_component.field_path]
                # Avoid parsing strings that are meant to be strings
                if not (isinstance(value, str) and valid_types == (str,)):
                    parsed_value = self._parse_yaml_if_possible(value)
                else:
                    parsed_value = value
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
            except ScannerError as e:  # "%Y-%m-%d'   # not valid yaml
                if "expected alphabetic or numeric character, but found '%'" in str(e):
                    return value
                raise e
        return value
