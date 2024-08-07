#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.utils.airbyte_secrets_utils import add_to_secrets, filter_secrets, get_secret_paths, get_secrets, update_secrets

SECRET_STRING_KEY = "secret_key1"
SECRET_STRING_VALUE = "secret_value"
SECRET_STRING_2_KEY = "secret_key2"
SECRET_STRING_2_VALUE = "second_secret_val"
SECRET_INT_KEY = "secret_int"
SECRET_INT_VALUE = 1337
NOT_SECRET_KEY = "not_a_secret"
NOT_SECRET_VALUE = "unimportant value"


flat_spec_with_secret = {"properties": {SECRET_STRING_KEY: {"type": "string", "airbyte_secret": True}, NOT_SECRET_KEY: {"type": "string"}}}
flat_config_with_secret = {SECRET_STRING_KEY: SECRET_STRING_VALUE, NOT_SECRET_KEY: NOT_SECRET_VALUE}

flat_spec_with_secret_int = {
    "properties": {SECRET_INT_KEY: {"type": "integer", "airbyte_secret": True}, NOT_SECRET_KEY: {"type": "string"}}
}
flat_config_with_secret_int = {SECRET_INT_KEY: SECRET_INT_VALUE, NOT_SECRET_KEY: NOT_SECRET_VALUE}

flat_spec_without_secrets = {"properties": {NOT_SECRET_KEY: {"type": "string"}}}
flat_config_without_secrets = {NOT_SECRET_KEY: NOT_SECRET_VALUE}

spec_with_oneof_secrets = {
    "properties": {
        SECRET_STRING_KEY: {"type": "string", "airbyte_secret": True},
        NOT_SECRET_KEY: {"type": "string"},
        "credentials": {
            "type": "object",
            "oneOf": [
                {
                    "type": "object",
                    "properties": {SECRET_STRING_2_KEY: {"type": "string", "airbyte_secret": True}, NOT_SECRET_KEY: {"type": "string"}},
                },
                {
                    "type": "object",
                    "properties": {SECRET_INT_KEY: {"type": "integer", "airbyte_secret": True}, NOT_SECRET_KEY: {"type": "string"}},
                },
            ],
        },
    }
}
config_with_oneof_secrets_1 = {
    SECRET_STRING_KEY: SECRET_STRING_VALUE,
    NOT_SECRET_KEY: NOT_SECRET_VALUE,
    "credentials": {SECRET_STRING_2_KEY: SECRET_STRING_2_VALUE},
}
config_with_oneof_secrets_2 = {
    SECRET_STRING_KEY: SECRET_STRING_VALUE,
    NOT_SECRET_KEY: NOT_SECRET_VALUE,
    "credentials": {SECRET_INT_KEY: SECRET_INT_VALUE},
}

spec_with_nested_secrets = {
    "properties": {
        SECRET_STRING_KEY: {"type": "string", "airbyte_secret": True},
        NOT_SECRET_KEY: {"type": "string"},
        "credentials": {
            "type": "object",
            "properties": {
                SECRET_STRING_2_KEY: {"type": "string", "airbyte_secret": True},
                NOT_SECRET_KEY: {"type": "string"},
                SECRET_INT_KEY: {"type": "integer", "airbyte_secret": True},
            },
        },
    }
}
config_with_nested_secrets = {
    SECRET_STRING_KEY: SECRET_STRING_VALUE,
    NOT_SECRET_KEY: NOT_SECRET_VALUE,
    "credentials": {SECRET_STRING_2_KEY: SECRET_STRING_2_VALUE, SECRET_INT_KEY: SECRET_INT_VALUE},
}


@pytest.mark.parametrize(
    ["spec", "expected"],
    [
        (flat_spec_with_secret, [[SECRET_STRING_KEY]]),
        (flat_spec_without_secrets, []),
        (flat_spec_with_secret_int, [[SECRET_INT_KEY]]),
        (spec_with_oneof_secrets, [[SECRET_STRING_KEY], ["credentials", SECRET_STRING_2_KEY], ["credentials", SECRET_INT_KEY]]),
        (spec_with_nested_secrets, [[SECRET_STRING_KEY], ["credentials", SECRET_STRING_2_KEY], ["credentials", SECRET_INT_KEY]]),
    ],
)
def test_get_secret_paths(spec, expected):
    assert get_secret_paths(spec) == expected, f"Expected {spec} to yield secret paths {expected}"


@pytest.mark.parametrize(
    ["spec", "config", "expected"],
    [
        (flat_spec_with_secret, flat_config_with_secret, [SECRET_STRING_VALUE]),
        (flat_spec_without_secrets, flat_config_without_secrets, []),
        (flat_spec_with_secret_int, flat_config_with_secret_int, [SECRET_INT_VALUE]),
        (spec_with_oneof_secrets, config_with_oneof_secrets_1, [SECRET_STRING_VALUE, SECRET_STRING_2_VALUE]),
        (spec_with_oneof_secrets, config_with_oneof_secrets_2, [SECRET_STRING_VALUE, SECRET_INT_VALUE]),
        (spec_with_nested_secrets, config_with_nested_secrets, [SECRET_STRING_VALUE, SECRET_STRING_2_VALUE, SECRET_INT_VALUE]),
    ],
)
def test_get_secrets(spec, config, expected):
    assert get_secrets(spec, config) == expected, f"Expected the spec {spec} and config {config} to produce {expected}"


def test_secret_filtering():
    sensitive_str = f"{SECRET_STRING_VALUE} {NOT_SECRET_VALUE} {SECRET_STRING_VALUE} {SECRET_STRING_2_VALUE}"

    update_secrets([])
    filtered = filter_secrets(sensitive_str)
    assert filtered == sensitive_str

    # the empty secret should not affect the result
    update_secrets([""])
    filtered = filter_secrets(sensitive_str)
    assert filtered == sensitive_str

    update_secrets([SECRET_STRING_VALUE, SECRET_STRING_2_VALUE])
    filtered = filter_secrets(sensitive_str)
    assert filtered == f"**** {NOT_SECRET_VALUE} **** ****"


def test_secrets_added_are_filtered():
    ADDED_SECRET = "only_a_secret_if_added"
    sensitive_str = f"{ADDED_SECRET} {NOT_SECRET_VALUE}"

    filtered = filter_secrets(sensitive_str)
    assert filtered == sensitive_str

    add_to_secrets(ADDED_SECRET)
    filtered = filter_secrets(sensitive_str)
    assert filtered == f"**** {NOT_SECRET_VALUE}"
