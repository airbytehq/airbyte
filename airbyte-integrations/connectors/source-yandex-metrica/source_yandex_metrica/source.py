#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Optional, Tuple

import pendulum

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import Sessions, Views, YandexMetricaStream


logger = logging.getLogger("airbyte")


class SourceYandexMetrica(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        authenticator = TokenAuthenticator(token=config.get("auth_token"))
        config["end_date"] = self.get_end_date(config=config)
        session = Sessions(authenticator=authenticator, config=config)
        views = Views(authenticator=authenticator, config=config)
        results = []
        for stream in (session, views):
            results.append(stream.evaluate_logrequest())
        if all(results):
            return True, None
        return False, "Please check provided credentials"

    def get_end_date(self, config) -> str:
        """Check if end date can be used, if not change to most recent date: yesterday"""
        start_date = pendulum.parse(config["start_date"]).date()
        end_date = pendulum.parse(config["end_date"]).date() if config.get("end_date") else None
        if end_date:
            if end_date < start_date:
                raise Exception("Start date cannot be later than end_date")
            if end_date > pendulum.yesterday().date():
                raise Exception("End date cannot be set later than yesterday")
        else:
            logger.info("Setting end date to yesterday")
            end_date = pendulum.yesterday().date()
        return str(end_date)

    def streams(self, config: Mapping[str, Any]) -> List[YandexMetricaStream]:
        authenticator = TokenAuthenticator(token=config.get("auth_token"))
        config["end_date"] = self.get_end_date(config=config)
        return [Sessions(authenticator=authenticator, config=config), Views(authenticator=authenticator, config=config)]
