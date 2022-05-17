#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Mapping

import yaml
from airbyte_cdk.sources.lcc.parsers.config_parser import ConfigParser


class YamlParser(ConfigParser):
    def parse(self, config_str: str) -> Mapping[str, Any]:
        config = yaml.safe_load(config_str)
        evaluated_config = dict()
        return self.preprocess_dict(config, evaluated_config, "")

    def preprocess_dict(self, config, evaluated_config, path):
        d = dict()
        for attribute, value in config.items():
            full_path = self.resolve_value(attribute, path)
            if full_path in evaluated_config:
                raise Exception(f"Databag already contains attribute={attribute}")
            processed_value = self.preprocess(value, evaluated_config, full_path)
            evaluated_config[full_path] = processed_value
            d[attribute] = processed_value
        return d

    def get_ref_key(self, s: str) -> str:
        ref_start = s.find("*ref(")
        if ref_start == -1:
            return None
        return s[ref_start + 5 : s.find(")")]

    def resolve_value(self, value, path):
        if path:
            return f"{path}.{value}"
        else:
            return value

    def preprocess(self, value, evaluated_config, path):
        if type(value) == str:
            ref_key = self.get_ref_key(value)
            if ref_key is None:
                return value
            else:
                return evaluated_config[ref_key]
        elif type(value) == dict:
            return self.preprocess_dict(value, evaluated_config, path)
        else:
            return value
