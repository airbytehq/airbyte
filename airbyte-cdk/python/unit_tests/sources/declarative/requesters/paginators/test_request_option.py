#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType


@pytest.mark.parametrize(
    "test_name, option_type, field_name, should_raise",
    [
        ("test_limit_path_no_field_name", RequestOptionType.path, None, False),
        ("test_limit_path_with_field_name", RequestOptionType.path, "field", True),
        ("test_limit_param_no_field_name", RequestOptionType.request_parameter, None, True),
        ("test_limit_param_with_field_name", RequestOptionType.request_parameter, "field", False),
        ("test_limit_header_no_field_name", RequestOptionType.header, None, True),
        ("test_limit_header_with_field_name", RequestOptionType.header, "field", False),
        ("test_limit_data_no_field_name", RequestOptionType.body_data, None, True),
        ("test_limit_data_with_field_name", RequestOptionType.body_data, "field", False),
        ("test_limit_json_no_field_name", RequestOptionType.body_json, None, True),
        ("test_limit_json_with_field_name", RequestOptionType.body_json, "field", False),
    ],
)
def test_request_option(test_name, option_type, field_name, should_raise):
    try:
        request_option = RequestOption(inject_into=option_type, field_name=field_name, options={})
        if should_raise:
            assert False
        assert request_option.field_name == field_name
        assert request_option.inject_into == option_type
    except ValueError:
        if not should_raise:
            assert False
