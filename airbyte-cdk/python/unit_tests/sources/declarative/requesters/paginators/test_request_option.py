#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType


@pytest.mark.parametrize(
    "test_name, option_type, field_name, expected_field_name",
    [
        ("test_limit_param_with_field_name", RequestOptionType.request_parameter, "field", "field"),
        ("test_limit_header_with_field_name", RequestOptionType.header, "field", "field"),
        ("test_limit_data_with_field_name", RequestOptionType.body_data, "field", "field"),
        ("test_limit_json_with_field_name", RequestOptionType.body_json, "field", "field"),
        ("test_limit_json_with_field_name", RequestOptionType.request_parameter, "since_{{ parameters['cursor_field'] }}", "since_updated_at"),
        ("test_limit_header_with_field_name", RequestOptionType.header, "since_{{ parameters['cursor_field'] }}", "since_updated_at"),
        ("test_limit_data_with_field_name", RequestOptionType.body_data, "since_{{ parameters['cursor_field'] }}", "since_updated_at"),
        ("test_limit_json_with_field_name", RequestOptionType.body_json, "since_{{ parameters['cursor_field'] }}", "since_updated_at"),
    ],
)
def test_request_option(test_name, option_type, field_name: str, expected_field_name: str):
    request_option = RequestOption(inject_into=option_type, field_name=field_name, parameters={"cursor_field": "updated_at"})
    assert request_option.field_name.eval({}) == expected_field_name
    assert request_option.inject_into == option_type
