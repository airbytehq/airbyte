#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import copy
import importlib
from typing import Any, Mapping, get_type_hints

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

    def build(self, class_name: str, config, **kwargs):
        if isinstance(class_name, str):
            class_ = self._get_class_from_fully_qualified_class_name(class_name)
        else:
            class_ = class_name

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

    def _create_subcomponent(self, k, v, kwargs, config, parent_class):
        if isinstance(v, dict) and "class_name" in v:
            # propagate kwargs to inner objects
            v["options"] = self._merge_dicts(kwargs.get("options", dict()), v.get("options", dict()))

            return self.create_component(v, config)()
        elif isinstance(v, dict) and "type" in v:
            v["options"] = self._merge_dicts(kwargs.get("options", dict()), v.get("options", dict()))
            object_type = v.pop("type")
            class_name = CLASS_TYPES_REGISTRY[object_type]
            v["class_name"] = class_name
            return self.create_component(v, config)()
        elif isinstance(v, dict):
            t = k
            type_hints = get_type_hints(parent_class.__init__)
            interface = type_hints.get(t)
            expected_type = DEFAULT_IMPLEMENTATIONS_REGISTRY.get(interface)
            if expected_type:
                v["class_name"] = expected_type
                v["options"] = self._merge_dicts(kwargs.get("options", dict()), v.get("options", dict()))
                return self.create_component(v, config)()
            else:
                return v
        elif isinstance(v, list):
            return [
                self._create_subcomponent(
                    k, sub, self._merge_dicts(kwargs.get("options", dict()), self._get_subcomponent_options(sub)), config, parent_class
                )
                for sub in v
            ]
        else:
            return v

    @staticmethod
    def _get_subcomponent_options(sub: Any):
        if isinstance(sub, dict):
            return sub.get("options", {})
        else:
            return {}
