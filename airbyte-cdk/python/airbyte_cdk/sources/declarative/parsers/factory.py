#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import copy
import importlib
from typing import Any, Mapping, Type, Union, get_type_hints

from airbyte_cdk.sources.declarative.create_partial import create
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.parsers.class_types_registry import CLASS_TYPES_REGISTRY
from airbyte_cdk.sources.declarative.parsers.default_implementation_registry import DEFAULT_IMPLEMENTATIONS_REGISTRY
from airbyte_cdk.sources.declarative.types import Config


class DeclarativeComponentFactory:
    def __init__(self):
        self._interpolator = JinjaInterpolation()

    def create_component(self, component_definition: Mapping[str, Any], config: Config):
        """

        :param component_definition: mapping defining the object to create. It should have at least one field: `class_name`
        :param config: Connector's config
        :return: the object to create
        """
        kwargs = copy.deepcopy(component_definition)
        class_name = kwargs.pop("class_name")
        return self.build(class_name, config, **kwargs)

    def build(self, class_or_class_name: Union[str, Type], config, **kwargs):
        if isinstance(class_or_class_name, str):
            class_ = self._get_class_from_fully_qualified_class_name(class_or_class_name)
        else:
            class_ = class_or_class_name

        # create components in options before propagating them
        if "options" in kwargs:
            kwargs["options"] = {k: self._create_subcomponent(k, v, kwargs, config, class_) for k, v in kwargs["options"].items()}

        updated_kwargs = {k: self._create_subcomponent(k, v, kwargs, config, class_) for k, v in kwargs.items()}

        return create(class_, config=config, **updated_kwargs)

    @staticmethod
    def _get_class_from_fully_qualified_class_name(class_name: str):
        split = class_name.split(".")
        module = ".".join(split[:-1])
        class_name = split[-1]
        return getattr(importlib.import_module(module), class_name)

    @staticmethod
    def _merge_dicts(d1, d2):
        return {**d1, **d2}

    def _create_subcomponent(self, key, definition, kwargs, config, parent_class):
        """
        There are 5 ways to define a component.
        1. dict with "class_name" field -> create an object of type "class_name"
        2. dict with "type" field -> lookup the `CLASS_TYPES_REGISTRY` to find the type of object and create an object of that type
        3. a dict with a type that can be inferred. If the parent class's constructor has type hints, we can infer the type of the object to create by looking up the `DEFAULT_IMPLEMENTATIONS_REGISTRY` map
        4. list: loop over the list and create objects for its items
        5. anything else -> return as is
        """
        if self.is_object_definition_with_class_name(definition):
            # propagate kwargs to inner objects
            definition["options"] = self._merge_dicts(kwargs.get("options", dict()), definition.get("options", dict()))

            return self.create_component(definition, config)()
        elif self.is_object_definition_with_type(definition):
            # If type is set instead of class_name, get the class_name from the CLASS_TYPES_REGISTRY
            definition["options"] = self._merge_dicts(kwargs.get("options", dict()), definition.get("options", dict()))
            object_type = definition.pop("type")
            class_name = CLASS_TYPES_REGISTRY[object_type]
            definition["class_name"] = class_name
            return self.create_component(definition, config)()
        elif isinstance(definition, dict):
            # Try to infer object type
            expected_type = self.get_default_type(key, parent_class)
            if expected_type:
                definition["class_name"] = expected_type
                definition["options"] = self._merge_dicts(kwargs.get("options", dict()), definition.get("options", dict()))
                return self.create_component(definition, config)()
            else:
                return definition
        elif isinstance(definition, list):
            return [
                self._create_subcomponent(
                    key, sub, self._merge_dicts(kwargs.get("options", dict()), self._get_subcomponent_options(sub)), config, parent_class
                )
                for sub in definition
            ]
        else:
            return definition

    @staticmethod
    def is_object_definition_with_class_name(definition):
        return isinstance(definition, dict) and "class_name" in definition

    @staticmethod
    def is_object_definition_with_type(definition):
        return isinstance(definition, dict) and "type" in definition

    @staticmethod
    def get_default_type(parameter_name, parent_class):
        type_hints = get_type_hints(parent_class.__init__)
        interface = type_hints.get(parameter_name)
        expected_type = DEFAULT_IMPLEMENTATIONS_REGISTRY.get(interface)
        return expected_type

    @staticmethod
    def _get_subcomponent_options(sub: Any):
        if isinstance(sub, dict):
            return sub.get("options", {})
        else:
            return {}
