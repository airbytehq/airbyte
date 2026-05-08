#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_microsoft_dataverse.dataverse import AirbyteType, convert_dataverse_type


@pytest.mark.parametrize(
    "dataverse_type,date_time_behavior,expected_result",
    [
        ("String", None, AirbyteType.String.value),
        ("Integer", None, AirbyteType.Integer.value),
        ("Virtual", None, None),
        ("Random", None, AirbyteType.String.value),
        ("DateTime", None, AirbyteType.Timestamp.value),
        ("DateTime", "UserLocal", AirbyteType.Timestamp.value),
        ("DateTime", "TimeZoneIndependent", AirbyteType.Timestamp.value),
        ("DateTime", "DateOnly", AirbyteType.Date.value),
    ],
)
def test_convert_dataverse_type(dataverse_type, date_time_behavior, expected_result):
    result = convert_dataverse_type(dataverse_type, date_time_behavior)
    assert result == expected_result
