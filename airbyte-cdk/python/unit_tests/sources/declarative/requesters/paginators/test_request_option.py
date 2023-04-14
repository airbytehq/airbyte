#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType


@pytest.mark.parametrize(
    "test_name, option_type, field_name",
    [
        ("test_limit_param_with_field_name", RequestOptionType.request_parameter, "field"),
        ("test_limit_header_with_field_name", RequestOptionType.header, "field"),
        ("test_limit_data_with_field_name", RequestOptionType.body_data, "field"),
        ("test_limit_json_with_field_name", RequestOptionType.body_json, "field"),
    ],
)
def test_request_option(test_name, option_type, field_name):
    request_option = RequestOption(inject_into=option_type, field_name=field_name, parameters={})
    assert request_option.field_name == field_name
    assert request_option.inject_into == option_type
