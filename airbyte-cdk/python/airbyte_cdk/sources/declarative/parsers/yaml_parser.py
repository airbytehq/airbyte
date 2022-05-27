#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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

        for attribute, value in input_mapping.items():
            if attribute == self.ref_tag:
                continue
            full_path = self.resolve_value(attribute, path)
            if full_path in evaluated_mapping:
                raise Exception(f"Databag already contains attribute={attribute} with path {full_path}")
            processed_value = self.preprocess(value, evaluated_mapping, full_path)
            evaluated_mapping[full_path] = processed_value
            d[attribute] = processed_value

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
        if type(value) == str:
            ref_key = self.get_ref_key(value)
            if ref_key is None:
                return value
            else:
                try:
                    ref_key_tuple = tuple(ref_key.split("."))
                    return evaluated_config[ref_key_tuple]
                except KeyError:
                    raise UndefinedReferenceException(path, ref_key)
        elif type(value) == dict:
            return self.preprocess_dict(value, evaluated_config, path)
        elif type(value) == list:
            return [self.preprocess(v, evaluated_config, path) for v in value]
        else:
            return value
