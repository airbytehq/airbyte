#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


def test_empty_url(components_module):
    url = ""
    parsed_url = components_module.remove_params_from_url(url=url, params=[])
    assert parsed_url == url


def test_does_not_raise_exception_for_invalid_url(components_module):
    url = "abcd"
    parsed_url = components_module.remove_params_from_url(url=url, params=["test"])
    assert parsed_url == url


def test_escaped_characters(components_module):
    url = "https://google.com?test=123%23%24%25%2A&test2=456"
    parsed_url = components_module.remove_params_from_url(url=url, params=["test3"])
    assert parsed_url == url


def test_no_params_url(components_module):
    url = "https://google.com"
    parsed_url = components_module.remove_params_from_url(url=url, params=["test"])
    assert parsed_url == url


def test_no_params_arg(components_module):
    url = "https://google.com?"
    parsed_url = components_module.remove_params_from_url(url=url, params=["test"])
    assert parsed_url == "https://google.com"


def test_partially_empty_params(components_module):
    url = "https://google.com?test=122&&"
    parsed_url = components_module.remove_params_from_url(url=url, params=[])
    assert parsed_url == "https://google.com?test=122"


def test_no_matching_params(components_module):
    url = "https://google.com?test=123"
    parsed_url = components_module.remove_params_from_url(url=url, params=["test2"])
    assert parsed_url == url


def test_removes_params(components_module):
    url = "https://google.com?test=123&test2=456"
    parsed_url = components_module.remove_params_from_url(url=url, params=["test2"])
    assert parsed_url == "https://google.com?test=123"
