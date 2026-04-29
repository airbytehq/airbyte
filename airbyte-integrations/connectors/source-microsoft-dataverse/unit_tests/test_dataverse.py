#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest import mock
from unittest.mock import MagicMock

import pytest
from source_microsoft_dataverse.dataverse import AirbyteType, convert_dataverse_type, get_datetime_behaviors


@pytest.mark.parametrize(
    "dataverse_type,datetime_behavior,expected_result",
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
def test_convert_dataverse_type(dataverse_type, datetime_behavior, expected_result):
    result = convert_dataverse_type(dataverse_type, datetime_behavior=datetime_behavior)
    assert result == expected_result


@mock.patch("source_microsoft_dataverse.dataverse.do_request")
def test_get_datetime_behaviors(mock_request):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "value": [
            {"LogicalName": "modifiedon", "DateTimeBehavior": {"Value": "UserLocal"}},
            {"LogicalName": "birthday", "DateTimeBehavior": {"Value": "DateOnly"}},
            {"LogicalName": "createdon", "DateTimeBehavior": {"Value": "TimeZoneIndependent"}},
        ]
    }
    mock_request.return_value = mock_response

    config_mock = MagicMock()
    result = get_datetime_behaviors(config_mock, "contact")

    assert result == {"modifiedon": "UserLocal", "birthday": "DateOnly", "createdon": "TimeZoneIndependent"}
    mock_request.assert_called_once_with(
        config_mock,
        "EntityDefinitions(LogicalName='contact')"
        "/Attributes/Microsoft.Dynamics.CRM.DateTimeAttributeMetadata"
        "?$select=LogicalName,DateTimeBehavior",
    )
