import pytest

from source_microsoft_dataverse.dataverse import convert_dataverse_type, AirbyteType


@pytest.mark.parametrize("dataverse_type,expected_result", [
    ("String", AirbyteType.String.value),
    ("Integer", AirbyteType.Integer.value),
    ("Virtual", None),
    ("Random", AirbyteType.String.value)
])
def test_convert_dataverse_type(dataverse_type, expected_result):
    result = convert_dataverse_type(dataverse_type)
    assert result == expected_result

