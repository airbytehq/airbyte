#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_google_analytics_v4.custom_reports_validator import CustomReportsValidator


@pytest.mark.parametrize(
    "custom_reports, expected",
    (
        ([{"name": "test", "dimensions": ["ga+test"], "metrics": ["ga!test"]}], "errors: incorrect field reference"),
        ([{"name": [], "dimensions": ["ga:test"], "metrics": ["ga:test"]}], "errors: type errors"),
        ([{"name": "test", "dimensions": ["ga:test"], "metrics": ["ga:test"], "added_field": "test"}], "errors: fields not permitted"),
        ([{"missing_name": "test", "dimensions": ["ga:test"], "metrics": ["ga:test"]}], "errors: fields required"),
    ),
    ids=["incorrrect field reference", "type_error", "not_permitted", "missing"],
)
def test_custom_reports_validator(custom_reports, expected):
    try:
        CustomReportsValidator(custom_reports).validate()
    except AirbyteTracedException as e:
        assert expected in str(e)
