#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Mapping

import yaml


def get_ref_key(s: str) -> str:
    ref_start = s.find("*ref(")
    if ref_start == -1:
        return None
    return s[ref_start + 5 : s.find(")")]


def resolve_value(value, path):
    if path:
        return f"{path}.{value}"
    else:
        return value


def preprocess(value, evaluated_config, path):
    if type(value) == str:
        ref_key = get_ref_key(value)
        if ref_key is None:
            return value
        else:
            return evaluated_config[ref_key]
    elif type(value) == dict:
        return preprocess_dict(value, evaluated_config, path)
    else:
        return value


def preprocess_dict(config, evaluated_config, path):
    for attribute, value in config.items():
        full_path = resolve_value(attribute, path)
        if full_path in evaluated_config:
            raise Exception(f"Databag already contains attribute={attribute}")
        evaluated_config[full_path] = preprocess(value, evaluated_config, full_path)
    return evaluated_config


def parse(config_string: str) -> Mapping[str, Any]:
    config = yaml.safe_load(config_string)
    evaluated_config = dict()
    return preprocess_dict(config, evaluated_config, "")


def test():
    content = """
    limit: 50
    """
    config = parse(content)
    assert config["limit"] == 50


def test_get_ref():
    s = """
    limit_ref: "*ref(limit)"
    """
    ref_key = get_ref_key(s)
    assert ref_key == "limit"


def test_get_ref_no_ref():
    s = """
    limit: 50
    """
    ref_key = get_ref_key(s)
    assert ref_key is None


def test_refer():
    content = """
    limit: 50
    limit_ref: "*ref(limit)"
    """
    config = parse(content)
    assert config["limit_ref"] == 50


def test_refer_to_inner():
    content = """
    dict:
      limit: 50
    limit_ref: "*ref(dict.limit)"
    """
    config = parse(content)
    assert config["limit_ref"] == 50


def test_refer_in_dict():
    content = """
    limit: 50
    offset_request_parameters:
      offset: "{{ next_page_token['offset'] }}"
      limit: "*ref(limit)"
    """
    config = parse(content)
    assert config["offset_request_parameters"]["limit"] == 50


def test_refer_to_dict():
    content = """
    limit: 50
    offset_request_parameters:
      offset: "{{ next_page_token['offset'] }}"
      limit: "*ref(limit)"
    offset_pagination_request_parameters:
      class: InterpolatedRequestParameterProvider
      request_parameters: "*ref(offset_request_parameters)"
    """
    config = parse(content)
    assert config["limit"] == 50
    assert config["offset_request_parameters"]["limit"] == 50
    assert len(config["offset_pagination_request_parameters"]) == 2
    # assert config["offset_pagination_request_parameters"]["request_parameters"]["limit"] == 50
