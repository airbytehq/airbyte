#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import importlib

from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation


class LowCodeComponentFactory:
    def __init__(self):
        self._interpolator = JinjaInterpolation()

    def build(self, config_mapping, parent_vars, config):
        print(f"config_mapping: {config_mapping}")
        fqcn = config_mapping["class_name"]
        split = fqcn.split(".")
        module = ".".join(split[:-1])
        class_name = split[-1]

        print(f"fqcn: {fqcn}")
        print(f"module: {module}")
        print(f"{class_name}")
        class_ = getattr(importlib.import_module(module), class_name)
        all_vars = self.merge_dicts(parent_vars, config_mapping.get("vars", {}))

        if "TokenAuthenticator" in class_name:
            print("creating auth")
            print(config_mapping)
            options = config_mapping["options"]
            interpolated_options = {k: self._interpolator.eval(v, all_vars, config) for k, v in options.items()}
            return class_(**interpolated_options)

        return class_(config_mapping["options"], all_vars, config)

    def merge_dicts(self, d1, d2):
        return {**d1, **d2}
