#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import copy
import importlib

from airbyte_cdk.sources.configurable.create_partial import create
from airbyte_cdk.sources.configurable.interpolation.jinja import JinjaInterpolation


class LowCodeComponentFactory:
    def __init__(self):
        self._interpolator = JinjaInterpolation()

    def create_component(self, component_definition, config):
        kwargs = copy.deepcopy(component_definition)
        class_name = kwargs.pop("class_name")

        return self.build(class_name, config, **kwargs)

    def build(self, class_name: str, config, **kwargs):
        fqcn = class_name
        split = fqcn.split(".")
        module = ".".join(split[:-1])
        class_name = split[-1]

        updated_kwargs = dict()
        for k, v in kwargs.items():
            if type(v) == dict and "class_name" in v:
                updated_kwargs[k] = self.create_component(v, config)()
            else:
                updated_kwargs[k] = v

        class_ = getattr(importlib.import_module(module), class_name)
        return create(class_, config=config, **updated_kwargs)

    def merge_dicts(self, d1, d2):
        return {**d1, **d2}
