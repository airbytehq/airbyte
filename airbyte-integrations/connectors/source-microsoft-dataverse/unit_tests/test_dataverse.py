#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest import mock
from unittest.mock import MagicMock

import pytest
from source_microsoft_dataverse.dataverse import (
    AirbyteType,
    _parse_batch_response,
    convert_dataverse_type,
    get_all_datetime_behaviors,
)


@pytest.mark.parametrize(
    "dataverse_type,datetime_behavior,expected_result",
    [
        pytest.param("String", None, AirbyteType.String.value, id="string"),
        pytest.param("Integer", None, AirbyteType.Integer.value, id="integer"),
        pytest.param("Virtual", None, None, id="virtual"),
        pytest.param("Random", None, AirbyteType.String.value, id="unknown_defaults_to_string"),
        pytest.param("DateTime", None, AirbyteType.Timestamp.value, id="datetime_no_behavior"),
        pytest.param("DateTime", "UserLocal", AirbyteType.Timestamp.value, id="datetime_userlocal"),
        pytest.param("DateTime", "TimeZoneIndependent", AirbyteType.Timestamp.value, id="datetime_tz_independent"),
        pytest.param("DateTime", "DateOnly", AirbyteType.Date.value, id="datetime_dateonly"),
    ],
)
def test_convert_dataverse_type(dataverse_type, datetime_behavior, expected_result):
    result = convert_dataverse_type(dataverse_type, datetime_behavior=datetime_behavior)
    assert result == expected_result


def test_parse_batch_response():
    boundary = "batchresponse_test-id"
    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/http\r\n"
        f"Content-Transfer-Encoding: binary\r\n"
        f"\r\n"
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: application/json; odata.metadata=minimal\r\n"
        f"OData-Version: 4.0\r\n"
        f"\r\n"
        f'{{"value":[{{"LogicalName":"modifiedon","DateTimeBehavior":{{"Value":"UserLocal"}}}},{{"LogicalName":"birthday","DateTimeBehavior":{{"Value":"DateOnly"}}}}]}}\r\n'
        f"--{boundary}\r\n"
        f"Content-Type: application/http\r\n"
        f"Content-Transfer-Encoding: binary\r\n"
        f"\r\n"
        f"HTTP/1.1 200 OK\r\n"
        f"Content-Type: application/json; odata.metadata=minimal\r\n"
        f"OData-Version: 4.0\r\n"
        f"\r\n"
        f'{{"value":[{{"LogicalName":"createdon","DateTimeBehavior":{{"Value":"TimeZoneIndependent"}}}}]}}\r\n'
        f"--{boundary}--\r\n"
    )

    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": f"multipart/mixed; boundary={boundary}"}
    mock_response.text = body

    result = _parse_batch_response(mock_response, ["contact", "account"])

    assert result == {
        "contact": {"modifiedon": "UserLocal", "birthday": "DateOnly"},
        "account": {"createdon": "TimeZoneIndependent"},
    }


def test_parse_batch_response_empty():
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.text = ""

    result = _parse_batch_response(mock_response, ["contact"])
    assert result == {}


@mock.patch("source_microsoft_dataverse.dataverse._execute_batch_datetime_request")
def test_get_all_datetime_behaviors_empty(mock_batch):
    result = get_all_datetime_behaviors(MagicMock(), [])
    assert result == {}
    mock_batch.assert_not_called()


@mock.patch("source_microsoft_dataverse.dataverse._execute_batch_datetime_request")
def test_get_all_datetime_behaviors_single_batch(mock_batch):
    mock_batch.return_value = {
        "contact": {"modifiedon": "UserLocal", "birthday": "DateOnly"},
        "account": {"createdon": "TimeZoneIndependent"},
    }

    config_mock = MagicMock()
    result = get_all_datetime_behaviors(config_mock, ["contact", "account"])

    assert result == {
        "contact": {"modifiedon": "UserLocal", "birthday": "DateOnly"},
        "account": {"createdon": "TimeZoneIndependent"},
    }
    mock_batch.assert_called_once_with(config_mock, ["contact", "account"])


@mock.patch("source_microsoft_dataverse.dataverse._execute_batch_datetime_request")
@mock.patch("source_microsoft_dataverse.dataverse.BATCH_SIZE", 2)
def test_get_all_datetime_behaviors_multiple_batches(mock_batch):
    mock_batch.side_effect = [
        {"entity1": {"f1": "UserLocal"}, "entity2": {"f2": "DateOnly"}},
        {"entity3": {"f3": "TimeZoneIndependent"}},
    ]

    config_mock = MagicMock()
    result = get_all_datetime_behaviors(config_mock, ["entity1", "entity2", "entity3"])

    assert result == {
        "entity1": {"f1": "UserLocal"},
        "entity2": {"f2": "DateOnly"},
        "entity3": {"f3": "TimeZoneIndependent"},
    }
    assert mock_batch.call_count == 2
