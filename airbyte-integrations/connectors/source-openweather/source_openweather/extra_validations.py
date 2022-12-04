#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping


def check_lat(lat_value) -> float:
    try:
        lat_value = float(lat_value)
    except (ValueError, TypeError):
        raise Exception("Wrong value for lat, it must be a decimal number between -90 and 90")
    if not -90 <= lat_value <= 90:
        raise Exception("Wrong value for lat, it must be between -90 and 90")
    return lat_value


def check_lon(lon_value) -> float:
    try:
        lon_value = float(lon_value)
    except (ValueError, TypeError):
        raise Exception("Wrong value for lon, it must be a decimal number between -180 and 180")

    if not -180 <= lon_value <= 180:
        raise Exception("Wrong value for lon, it must be between -180 and 180")
    return lon_value


def validate(config: Mapping[str, Any]) -> Mapping[str, Any]:
    valid_config = {**config}
    valid_config["lat"] = check_lat(valid_config["lat"])
    valid_config["lon"] = check_lon(valid_config["lon"])
    return valid_config
