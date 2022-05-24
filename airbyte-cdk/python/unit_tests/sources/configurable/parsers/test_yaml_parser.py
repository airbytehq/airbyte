#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import pytest
from airbyte_cdk.sources.configurable.parsers.yaml_parser import YamlParser

parser = YamlParser()


def test():
    content = """
    limit: 50
    """
    config = parser.parse(content)
    assert config["limit"] == 50


def test_get_ref():
    s = """
    limit_ref: "*ref(limit)"
    """
    ref_key = parser.get_ref_key(s)
    assert ref_key == "limit"


def test_get_ref_no_ref():
    s = """
    limit: 50
    """
    ref_key = parser.get_ref_key(s)
    assert ref_key is None


def test_refer():
    content = """
    limit: 50
    limit_ref: "*ref(limit)"
    """
    config = parser.parse(content)
    assert config["limit_ref"] == 50


def test_refer_to_inner():
    content = """
    dict:
      limit: 50
    limit_ref: "*ref(dict.limit)"
    """
    config = parser.parse(content)
    assert config["limit_ref"] == 50


def test_refer_to_non_existant_struct():
    content = """
    dict:
      limit: 50
    limit_ref: "*ref(not_dict)"
    """
    with pytest.raises(KeyError):
        parser.parse(content)


def test_refer_in_dict():
    content = """
    limit: 50
    offset_request_parameters:
      offset: "{{ next_page_token['offset'] }}"
      limit: "*ref(limit)"
    """
    config = parser.parse(content)
    assert config["offset_request_parameters"]["offset"] == "{{ next_page_token['offset'] }}"
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
    config = parser.parse(content)
    assert config["limit"] == 50
    assert config["offset_request_parameters"]["limit"] == 50
    assert len(config["offset_pagination_request_parameters"]) == 2
    assert config["offset_pagination_request_parameters"]["request_parameters"]["limit"] == 50
    assert config["offset_pagination_request_parameters"]["request_parameters"]["offset"] == "{{ next_page_token['offset'] }}"


def test_refer_and_overwrite():
    content = """
    limit: 50
    custom_limit: 25
    offset_request_parameters:
      offset: "{{ next_page_token['offset'] }}"
      limit: "*ref(limit)"
    custom_request_parameters:
      partial: "*ref(offset_request_parameters)"
      limit: "*ref(custom_limit)"
    """
    config = parser.parse(content)
    assert config["offset_request_parameters"]["limit"] == 50
    assert config["custom_request_parameters"]["limit"] == 25

    assert config["offset_request_parameters"]["offset"] == "{{ next_page_token['offset'] }}"
    assert config["custom_request_parameters"]["offset"] == "{{ next_page_token['offset'] }}"
