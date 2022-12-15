#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from . import extra_validations, streams


class SourceOpenWeather(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            valid_config = extra_validations.validate(config)
            params = {
                "appid": valid_config["appid"],
                "lat": valid_config["lat"],
                "lon": valid_config["lon"],
                "lang": valid_config.get("lang"),
                "units": valid_config.get("units"),
            }
            params = {k: v for k, v in params.items() if v is not None}
            resp = requests.get(f"{streams.OneCall.url_base}onecall", params=params)
            status = resp.status_code
            if status == 200:
                return True, None
            else:
                message = resp.json().get("message")
                return False, message
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        valid_config = extra_validations.validate(config)
        return [
            streams.OneCall(
                appid=valid_config["appid"],
                lat=valid_config["lat"],
                lon=valid_config["lon"],
                lang=valid_config.get("lang"),
                units=valid_config.get("units"),
            )
        ]
