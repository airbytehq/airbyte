#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_openweather import extra_validations


@pytest.mark.parametrize(
    "lat_value, error_message",
    [
        ("1", None),
        (1, None),
        ("-12.3", None),
        ("-91", "Wrong value for lat, it must be between -90 and 90"),
        ("91", "Wrong value for lat, it must be between -90 and 90"),
        ("1,2", "Wrong value for lat, it must be a decimal number between -90 and 90"),
        ("foo", "Wrong value for lat, it must be a decimal number between -90 and 90"),
        (["not_string"], "Wrong value for lat, it must be a decimal number between -90 and 90"),
    ],
)
def test_check_lat(lat_value, error_message):
    if error_message:
        with pytest.raises(Exception, match=error_message):
            extra_validations.check_lat(lat_value)
    else:
        assert extra_validations.check_lat(lat_value) == float(lat_value)


@pytest.mark.parametrize(
    "lon_value, error_message",
    [
        ("1", None),
        (1, None),
        ("-92.3", None),
        ("-191", "Wrong value for lon, it must be between -180 and 180"),
        ("191", "Wrong value for lon, it must be between -180 and 180"),
        ("1,2", "Wrong value for lon, it must be a decimal number between -180 and 180"),
        ("foo", "Wrong value for lon, it must be a decimal number between -180 and 180"),
        (["not_string"], "Wrong value for lon, it must be a decimal number between -180 and 180"),
    ],
)
def test_check_lon(lon_value, error_message):
    if error_message:
        with pytest.raises(Exception, match=error_message):
            extra_validations.check_lon(lon_value)
    else:
        assert extra_validations.check_lon(lon_value) == float(lon_value)


def test_validate(mocker):
    check_lat_mock = mocker.patch("source_openweather.extra_validations.check_lat")
    check_lat_mock.return_value = 1.0
    check_lon_mock = mocker.patch("source_openweather.extra_validations.check_lon")
    check_lon_mock.return_value = 1.0

    config_to_validate = {"appid": "foo", "lat": "1", "lon": "1"}
    expected_valid_config = {"appid": "foo", "lat": 1.0, "lon": 1.0}

    valid_config = extra_validations.validate(config_to_validate)
    assert isinstance(valid_config, dict)
    assert valid_config == expected_valid_config
    check_lat_mock.assert_called_with("1")
    check_lon_mock.assert_called_with("1")
