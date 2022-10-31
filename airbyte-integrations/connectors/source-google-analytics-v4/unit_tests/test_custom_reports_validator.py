#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_google_analytics_v4.custom_reports_validator import CustomReportsValidator


@pytest.mark.parametrize(
    "custom_reports, expected",
    (
        ([{"name": [], "dimensions": ["test"], "metrics": ["test"]}], "errors: type errors"),
        ([{"name": "test", "dimensions": ["test"], "metrics": ["test"], "added_field": "test"}], "errors: fields not permitted"),
        ([{"missing_name": "test", "dimensions": ["test"], "metrics": ["test"]}], "errors: fields required"),
    ),
    ids=["type_error", "not_permitted", "missing"],
)
def test_custom_reports_validator(custom_reports, expected):
    try:
        CustomReportsValidator(custom_reports).validate()
    except AirbyteTracedException as e:
        assert expected in str(e)
