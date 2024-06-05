#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType


@pytest.mark.parametrize(
    "option_type, field_name, expected_field_name",
    [
        (RequestOptionType.request_parameter, "field", "field"),
        (RequestOptionType.header, "field", "field"),
        (RequestOptionType.body_data, "field", "field"),
        (RequestOptionType.body_json, "field", "field"),
        (RequestOptionType.request_parameter, "since_{{ parameters['cursor_field'] }}", "since_updated_at"),
        (RequestOptionType.header, "since_{{ parameters['cursor_field'] }}", "since_updated_at"),
        (RequestOptionType.body_data, "since_{{ parameters['cursor_field'] }}", "since_updated_at"),
        (RequestOptionType.body_json, "since_{{ parameters['cursor_field'] }}", "since_updated_at"),
        (RequestOptionType.request_parameter, "since_{{ config['cursor_field'] }}", "since_created_at"),
        (RequestOptionType.header, "since_{{ config['cursor_field'] }}", "since_created_at"),
        (RequestOptionType.body_data, "since_{{ config['cursor_field'] }}", "since_created_at"),
        (RequestOptionType.body_json, "since_{{ config['cursor_field'] }}", "since_created_at"),
    ],
    ids=[
        "test_limit_param_with_field_name",
        "test_limit_header_with_field_name",
        "test_limit_data_with_field_name",
        "test_limit_json_with_field_name",
        "test_limit_param_with_parameters_interpolation",
        "test_limit_header_with_parameters_interpolation",
        "test_limit_data_with_parameters_interpolation",
        "test_limit_json_with_parameters_interpolation",
        "test_limit_param_with_config_interpolation",
        "test_limit_header_with_config_interpolation",
        "test_limit_data_with_config_interpolation",
        "test_limit_json_with_config_interpolation",
    ],
)
def test_request_option(option_type: RequestOptionType, field_name: str, expected_field_name: str):
    request_option = RequestOption(inject_into=option_type, field_name=field_name, parameters={"cursor_field": "updated_at"})
    assert request_option.field_name.eval({"cursor_field": "created_at"}) == expected_field_name
    assert request_option.inject_into == option_type
