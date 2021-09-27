#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
from base_python.cdk.utils.casing import camel_to_snake


@pytest.mark.parametrize(
    ("camel_cased", "snake_cased"),
    [
        ["HTTPStream", "http_stream"],
        ["already_snake", "already_snake"],
        ["ProperCased", "proper_cased"],
        ["camelCased", "camel_cased"],
        ["veryVeryLongCamelCasedName", "very_very_long_camel_cased_name"],
        ["throw2NumbersH3re", "throw2_numbers_h3re"],
    ],
)
def test_camel_to_snake(camel_cased, snake_cased):
    assert camel_to_snake(camel_cased) == snake_cased
