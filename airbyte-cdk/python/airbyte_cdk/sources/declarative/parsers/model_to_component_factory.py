#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Callable, List, Literal, Mapping, Type, Union

from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.models.declarative_component_schema import CheckStream as CheckStreamModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.models.declarative_component_schema import Spec as SpecModel
from airbyte_cdk.sources.declarative.spec import Spec
from airbyte_cdk.sources.declarative.types import Config
from pydantic import BaseModel

ComponentDefinition: Union[Literal, Mapping, List]


def create_check_stream(model: CheckStreamModel, config: Config):
    return CheckStream(model.stream_names, options={})


def create_declarative_stream(model: DeclarativeStreamModel, config: Config):
    # todo this is just a stub temporarily, but should actually return DeclarativeStream but that requires building the whole object
    return {}


def create_spec(model: SpecModel, config: Config):
    return Spec(connection_specification=model.connection_specification, documentation_url=model.documentation_url, options={})


class ModelToComponentFactory:
    def create_component(self, model_type: Type[BaseModel], component_definition: ComponentDefinition, config: Config) -> type:
        component_type = component_definition.get("type")
        if component_definition.get("type") != model_type.__name__:
            raise ValueError(f"Expected manifest component of type {model_type}, but received {component_type} instead")

        declarative_component_model = model_type.parse_obj(component_definition)

        if not isinstance(declarative_component_model, model_type):
            raise ValueError(f"Expected DeclarativeStream component, but received {declarative_component_model.__class__.__name__}")

        return self.create_component_from_model(model=declarative_component_model, config=config)

    @staticmethod
    def create_component_from_model(model: BaseModel, config: Config) -> type:
        if model.__class__ not in PYDANTIC_MODEL_TO_CONSTRUCTOR:
            raise ValueError(f"{model.__class__} with attributes {model} is not a valid component type")
        component_constructor = PYDANTIC_MODEL_TO_CONSTRUCTOR.get(model.__class__)
        return component_constructor(model=model, config=config)


PYDANTIC_MODEL_TO_CONSTRUCTOR: Mapping[Type[BaseModel], Callable] = {
    CheckStreamModel: create_check_stream,
    DeclarativeStreamModel: create_declarative_stream,
    SpecModel: create_spec,
}
