import pytest
from source_google_analytics_data_api.utils import (
    serialize_to_date_string,  # Replace 'your_module' with the actual module where serialize_to_date_string is defined
)


def test_serialize_to_date_string_yearWeek():
    assert serialize_to_date_string("202105", "%Y-%m-%d", "yearWeek") == "2021-02-01"


def test_serialize_to_date_string_yearMonth():
    assert serialize_to_date_string("202105", "%Y-%m-%d", "yearMonth") == "2021-05-01"


def test_serialize_to_date_string_invalid_type():
    with pytest.raises(ValueError):  # Assumes that an invalid date_type will raise a ValueError
        serialize_to_date_string("202105", "%Y-%m-%d", "invalidType")
