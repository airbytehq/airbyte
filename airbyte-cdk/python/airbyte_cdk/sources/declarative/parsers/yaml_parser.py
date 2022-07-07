#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from typing import Any, Mapping

import yaml
from airbyte_cdk.sources.declarative.parsers.config_parser import ConfigParser
from airbyte_cdk.sources.declarative.parsers.undefined_reference_exception import UndefinedReferenceException


class YamlParser(ConfigParser):
    ref_tag = "ref"

    def parse(self, config_str: str) -> Mapping[str, Any]:
        """
        Parses a yaml file and dereferences string in the form "*ref({reference)"
        to {reference}
        :param config_str: yaml string to parse
        :return:
        """
        input_mapping = yaml.safe_load(config_str)
        evaluated_config = {}
        return self.preprocess_dict(input_mapping, evaluated_config, "")

    def preprocess_dict(self, input_mapping, evaluated_mapping, path):
        """
        :param input_mapping: mapping produced by parsing yaml
        :param evaluated_mapping: mapping produced by dereferencing the content of input_mapping
        :param path: curent path in configuration traversal
        :return:
        """
        d = {}
        if self.ref_tag in input_mapping:
            partial_ref_string = input_mapping[self.ref_tag]
            d = deepcopy(self.preprocess(partial_ref_string, evaluated_mapping, path))

        for key, value in input_mapping.items():
            if key == self.ref_tag:
                continue
            full_path = self.resolve_value(key, path)
            if full_path in evaluated_mapping:
                raise Exception(f"Databag already contains key={key} with path {full_path}")
            processed_value = self.preprocess(value, evaluated_mapping, full_path)
            evaluated_mapping[full_path] = processed_value
            d[key] = processed_value

        return d

    def get_ref_key(self, s: str) -> str:
        ref_start = s.find("*ref(")
        if ref_start == -1:
            return None
        return s[ref_start + 5 : s.find(")")]

    def resolve_value(self, value, path):
        if path:
            return *path, value
        else:
            return (value,)

    def preprocess(self, value, evaluated_config, path):
        if isinstance(value, str):
            ref_key = self.get_ref_key(value)
            if ref_key is None:
                return value
            else:
                """
                references are ambiguous because one could define a key containing with `.`
                in this example, we want to refer to the limit key in the dict object:
                    dict:
                        limit: 50
                    limit_ref: "*ref(dict.limit)"

                whereas here we want to access the `nested.path` value.
                  nested:
                    path: "first one"
                  nested.path: "uh oh"
                  value: "ref(nested.path)

                to resolve the ambiguity, we try looking for the reference key at the top level, and then traverse the structs downward
                until we find a key with the given path, or until there is nothing to traverse.
                """
                key = (ref_key,)
                while key[-1]:
                    if key in evaluated_config:
                        return evaluated_config[key]
                    else:
                        split = key[-1].split(".")
                        key = *key[:-1], split[0], ".".join(split[1:])
                raise UndefinedReferenceException(path, ref_key)
        elif isinstance(value, dict):
            return self.preprocess_dict(value, evaluated_config, path)
        elif type(value) == list:
            evaluated_list = [self.preprocess(v, evaluated_config, path) for v in value]
            return evaluated_list
        else:
            return value
