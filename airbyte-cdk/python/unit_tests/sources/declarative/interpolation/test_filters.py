#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import base64
import hashlib

import pytest
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation

interpolation = JinjaInterpolation()


def test_hash_md5_no_salt() -> None:
    input_string = "abcd"
    s = "{{ '%s' | hash('md5') }}" % input_string
    filter_hash = interpolation.eval(s, config={})

    # compute expected hash calling hashlib directly
    hash_obj = hashlib.md5()
    hash_obj.update(str(input_string).encode("utf-8"))
    hashlib_computed_hash = hash_obj.hexdigest()

    assert filter_hash == hashlib_computed_hash


def test_hash_md5_on_numeric_value() -> None:
    input_value = 123.456
    s = "{{ %f | hash('md5') }}" % input_value
    filter_hash = interpolation.eval(s, config={})

    # compute expected hash calling hashlib directly
    hash_obj = hashlib.md5()
    hash_obj.update(str(input_value).encode("utf-8"))
    hashlib_computed_hash = hash_obj.hexdigest()

    assert filter_hash == hashlib_computed_hash


def test_hash_md5_with_salt() -> None:
    input_string = "test_input_string"
    input_salt = "test_input_salt"

    s = "{{ '%s' | hash('md5', '%s' ) }}" % (input_string, input_salt)
    filter_hash = interpolation.eval(s, config={})

    # compute expected value calling hashlib directly
    hash_obj = hashlib.md5()
    hash_obj.update(str(input_string + input_salt).encode("utf-8"))
    hashlib_computed_hash = hash_obj.hexdigest()

    assert filter_hash == hashlib_computed_hash


@pytest.mark.parametrize(
    "input_string",
    ["test_input_client_id", "some_client_secret_1", "12345", "775.78"],
)
def test_base64encode(input_string: str) -> None:
    s = "{{ '%s' | base64encode }}" % input_string
    filter_base64encode = interpolation.eval(s, config={})

    # compute expected base64encode calling base64 library directly
    base64_obj = base64.b64encode(input_string.encode("utf-8")).decode()

    assert filter_base64encode == base64_obj


@pytest.mark.parametrize(
    "input_string, expected_string",
    [
        ("aW5wdXRfc3RyaW5n", "input_string"),
        ("YWlyYnl0ZQ==", "airbyte"),
        ("cGFzc3dvcmQ=", "password"),
    ],
)
def test_base64decode(input_string: str, expected_string: str) -> None:
    s = "{{ '%s' | base64decode }}" % input_string
    filter_base64decode = interpolation.eval(s, config={})

    assert filter_base64decode == expected_string


def test_regex_search_valid() -> None:
    expression_with_regex = "{{ '<https://this-is-test-link.com/?page=2>; rel=\"next\"' | regex_search('<(.*)>; rel=.*') }}"

    val = interpolation.eval(expression_with_regex, {})
    assert val == "https://this-is-test-link.com/?page=2"


def test_regex_search_no_match_group() -> None:
    # If no group is set in the regular expression, the result will be an empty string
    expression_with_regex = "{{ '<https://this-is-test-link.com/?page=2>; rel=\"next\"' | regex_search('<.*>; rel=.*') }}"

    val = interpolation.eval(expression_with_regex, {})
    assert val is None


def test_regex_search_no_match() -> None:
    # If no group is set in the regular expression, the result will be an empty string
    expression_with_regex = "{{ '<https://this-is-test-link.com/?page=2>; rel=\"next\"' | regex_search('WATWATWAT') }}"

    val = interpolation.eval(expression_with_regex, {})

    assert val is None
