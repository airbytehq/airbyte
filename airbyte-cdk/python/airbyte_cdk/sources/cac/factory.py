#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation

if TYPE_CHECKING:
    from airbyte_cdk.sources.cac.types import ComponentDefinition, Config, Options, Vars


class LowCodeComponentFactory:
    def __init__(self):
        self._interpolator = JinjaInterpolation()

    def create_component(self, component_definition: ComponentDefinition, vars: Vars, config: Config):
        class_name = component_definition["class_name"]
        component_vars = component_definition.get("vars", {})
        options = component_definition.get("options", {})
        return self.build(class_name=class_name, options=options, parent_vars=vars, inner_vars=component_vars, config=config)

    def build(self, class_name: str, options: Options, parent_vars: Vars, inner_vars: Vars, config: Config):
        fqcn = class_name  # config_mapping["class_name"]
        split = fqcn.split(".")
        module = ".".join(split[:-1])
        class_name = split[-1]

        class_ = getattr(importlib.import_module(module), class_name)
        all_vars = self.merge_dicts(parent_vars, inner_vars)

        if "TokenAuthenticator" in class_name:
            interpolated_options = {k: self._interpolator.eval(v, all_vars, config) for k, v in options.items()}
            return class_(**interpolated_options)

        return class_(vars=all_vars, config=config, **options)

    def merge_dicts(self, d1, d2):
        return {**d1, **d2}
