#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from abc import abstractmethod
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Union, Type

import dpath
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation import InterpolatedBoolean, InterpolatedString
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.types import Config

if TYPE_CHECKING:
    from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream


@dataclass
class ComponentsParser:
    @abstractmethod
    def parse_stream_components(self, stream_template_config: Dict[str, Any]):
        pass


@dataclass(frozen=True)
class MapComponentsDefinition:
    """Defines the component to update on a stream config"""

    key: str
    value: Union[InterpolatedString, str]
    value_type: Optional[Type[Any]]
    parameters: InitVar[Mapping[str, Any]]
    condition: str = ""


@dataclass(frozen=True)
class ParsedMapComponentsDefinition:
    """Defines the component to update on a stream config"""

    key: str
    value: Union[InterpolatedString, str]
    value_type: Optional[Type[Any]]
    parameters: InitVar[Mapping[str, Any]]
    condition: str = ""


@dataclass
class DynamicComponentsParser(ComponentsParser):
    components_values_stream: "DeclarativeStream"
    config: Config
    components_mapping: List[MapComponentsDefinition]
    parameters: InitVar[Mapping[str, Any]]
    _parsed_components_mapping: List[ParsedMapComponentsDefinition] = field(init=False, repr=False, default_factory=list)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        for component_mapping in self.components_mapping:

            condition = component_mapping.condition if component_mapping.condition else True

            if not isinstance(component_mapping.value, InterpolatedString):
                if not isinstance(component_mapping.value, str):
                    raise f"Expected a string value for the AddFields transformation: {component_mapping}"
                else:
                    self._parsed_components_mapping.append(
                        ParsedMapComponentsDefinition(
                            component_mapping.key,
                            InterpolatedString.create(component_mapping.value, parameters=parameters),
                            value_type=component_mapping.value_type,
                            condition=InterpolatedBoolean(condition=condition, parameters=parameters),
                            parameters=parameters,
                        )
                    )
            else:
                self._parsed_components_mapping.append(
                    ParsedMapComponentsDefinition(
                        component_mapping.key,
                        component_mapping.value,
                        value_type=component_mapping.value_type,
                        condition=InterpolatedBoolean(condition=condition, parameters=parameters),
                        parameters={},
                    )
                )

    def _update_config_specific_key(self, target_dict, target_key, target_value, interpolated_condition=None, **kwargs):
        kwargs["td"] = target_dict
        condition = interpolated_condition.eval(self.config, **kwargs) if interpolated_condition else True

        for key, value in target_dict.items():
            if key == target_key and condition:
                target_dict[key] = target_value
            elif isinstance(value, dict):
                target_dict[key] = self._update_config_specific_key(value, target_key, target_value, interpolated_condition, **kwargs)
            elif isinstance(value, list):
                target_dict[key] = [
                    self._update_config_specific_key(item, target_key, target_value, interpolated_condition, **kwargs)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]

        return target_dict

    def parse_stream_components(self, stream_template_config: Dict[str, Any]) -> Dict[str, Any]:
        kwargs = {"stream_template_config": stream_template_config}

        for components_value in self.components_values_stream.read_only_records():
            updated_config = deepcopy(stream_template_config)
            kwargs["components_value"] = components_value

            for parsed_component_mapping in self._parsed_components_mapping:
                valid_types = (parsed_component_mapping.value_type,) if parsed_component_mapping.value_type else None
                value = parsed_component_mapping.value.eval(self.config, valid_types=valid_types, **kwargs)
                key = parsed_component_mapping.key
                interpolated_condition = parsed_component_mapping.condition

                updated_config = self._update_config_specific_key(
                    updated_config, key, value, interpolated_condition=interpolated_condition, **kwargs
                )

            yield updated_config
