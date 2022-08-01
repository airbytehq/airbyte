#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from typing import Any, Mapping, Tuple, Union

import yaml
from airbyte_cdk.sources.declarative.parsers.config_parser import ConnectionDefinitionParser
from airbyte_cdk.sources.declarative.parsers.undefined_reference_exception import UndefinedReferenceException
from airbyte_cdk.sources.declarative.types import ConnectionDefinition


class YamlParser(ConnectionDefinitionParser):
    """
    Parses a Yaml string to a ConnectionDefinition

    In addition to standard Yaml parsing, the input_string can contain references to values previously defined.
    This parser will dereference these values to produce a complete ConnectionDefinition.

    References can be defined using a *ref(<arg>) string.
    ```
    key: 1234
    reference: "*ref(key)"
    ```
    will produce the following definition:
    ```
    key: 1234
    reference: 1234
    ```
    This also works with objects:
    ```
    key_value_pairs:
      k1: v1
      k2: v2
    same_key_value_pairs: "*ref(key_value_pairs)"
    ```
    will produce the following definition:
    ```
    key_value_pairs:
      k1: v1
      k2: v2
    same_key_value_pairs:
      k1: v1
      k2: v2
    ```

    The $ref keyword can be used to refer to an object and enhance it with addition key-value pairs
    ```
    key_value_pairs:
      k1: v1
      k2: v2
    same_key_value_pairs:
      $ref: "*ref(key_value_pairs)"
      k3: v3
    ```
    will produce the following definition:
    ```
    key_value_pairs:
      k1: v1
      k2: v2
    same_key_value_pairs:
      k1: v1
      k2: v2
      k3: v3
    ```

    References can also point to nested values.
    Nested references are ambiguous because one could define a key containing with `.`
    in this example, we want to refer to the limit key in the dict object:
    ```
    dict:
        limit: 50
    limit_ref: "*ref(dict.limit)"
    ```
    will produce the following definition:
    ```
    dict
        limit: 50
    limit-ref: 50
    ```

    whereas here we want to access the `nested.path` value.
    ```
    nested:
        path: "first one"
    nested.path: "uh oh"
    value: "ref(nested.path)
    ```
    will produce the following definition:
    ```
    nested:
        path: "first one"
    nested.path: "uh oh"
    value: "uh oh"
    ```

    to resolve the ambiguity, we try looking for the reference key at the top level, and then traverse the structs downward
    until we find a key with the given path, or until there is nothing to traverse.
    """

    ref_tag = "$ref"

    def parse(self, connection_definition_str: str) -> ConnectionDefinition:
        """
        Parses a yaml file and dereferences string in the form "*ref({reference)"
        to {reference}
        :param connection_definition_str: yaml string to parse
        :return: The ConnectionDefinition parsed from connection_definition_str
        """
        input_mapping = yaml.safe_load(connection_definition_str)
        evaluated_definition = {}
        return self._preprocess_dict(input_mapping, evaluated_definition, "")

    def _preprocess_dict(self, input_mapping: Mapping[str, Any], evaluated_mapping: Mapping[str, Any], path: Union[str, Tuple[str]]):

        """
        :param input_mapping: mapping produced by parsing yaml
        :param evaluated_mapping: mapping produced by dereferencing the content of input_mapping
        :param path: curent path in configuration traversal
        :return:
        """
        d = {}
        if self.ref_tag in input_mapping:
            partial_ref_string = input_mapping[self.ref_tag]
            d = deepcopy(self._preprocess(partial_ref_string, evaluated_mapping, path))

        for key, value in input_mapping.items():
            if key == self.ref_tag:
                continue
            full_path = self._resolve_value(key, path)
            if full_path in evaluated_mapping:
                raise Exception(f"Databag already contains key={key} with path {full_path}")
            processed_value = self._preprocess(value, evaluated_mapping, full_path)
            evaluated_mapping[full_path] = processed_value
            d[key] = processed_value

        return d

    def _get_ref_key(self, s: str) -> str:
        ref_start = s.find("*ref(")
        if ref_start == -1:
            return None
        return s[ref_start + 5 : s.find(")")]

    def _resolve_value(self, value: str, path):
        if path:
            return *path, value
        else:
            return (value,)

    def _preprocess(self, value, evaluated_config: Mapping[str, Any], path):
        if isinstance(value, str):
            ref_key = self._get_ref_key(value)
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
            return self._preprocess_dict(value, evaluated_config, path)
        elif type(value) == list:
            evaluated_list = [
                # pass in elem's path instead of the list's path
                self._preprocess(v, evaluated_config, self._get_path_for_list_item(path, index))
                for index, v in enumerate(value)
            ]
            # Add the list's element to the evaluated config so they can be referenced
            for index, elem in enumerate(evaluated_list):
                evaluated_config[self._get_path_for_list_item(path, index)] = elem
            return evaluated_list
        else:
            return value

    def _get_path_for_list_item(self, path, index):
        # An elem's path is {path_to_list}[{index}]
        if len(path) > 1:
            return path[:-1], f"{path[-1]}[{index}]"
        else:
            return (f"{path[-1]}[{index}]",)
