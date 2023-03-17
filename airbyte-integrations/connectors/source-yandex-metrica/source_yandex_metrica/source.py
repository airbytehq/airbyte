#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import Sessions, Views, YandexMetricaStream
import pendulum

logger = logging.getLogger("airbyte")


class SourceYandexMetrica(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # evaluate_views_stream = Evaluate(
            #     **{
            #         "counter_id": config["counter_id"],
            #         "params": {
            #             "start_date": config["start_date"],
            #             "end_date": self.get_end_date(config),
            #         },
            #         "source": "hits",
            #         "authenticator": TokenAuthenticator(token=config["auth_token"]),
            #     }
            # )
            # evaluate_sessions_stream = Evaluate(
            #     **{
            #         "counter_id": config["counter_id"],
            #         "params": {
            #             "start_date": config["start_date"],
            #             "end_date": self.get_end_date(config),
            #         },
            #         "source": "visits",
            #         "authenticator": TokenAuthenticator(token=config["auth_token"]),
            #     }
            # )
            # next(evaluate_views_stream.read_records(sync_mode=SyncMode.full_refresh))
            # next(evaluate_sessions_stream.read_records(sync_mode=SyncMode.full_refresh))

            return True, None
        except Exception as e:
            return False, e

    def get_end_date(self, config) -> str:
        "Check if end date can be used, if not change to most recent date: yesterday"
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
        authenticator = TokenAuthenticator(token=config["auth_token"])
        views_stream_args = {
            "counter_id": config["counter_id"],
            "params": {
                "start_date": config["start_date"],
                "end_date": self.get_end_date(config),
            },
            "authenticator": authenticator,
        }
        sessions_stream_args = {
            "counter_id": config["counter_id"],
            "params": {
                "start_date": config["start_date"],
                "end_date": self.get_end_date(config),
            },
            "authenticator": authenticator,
        }
        return [Sessions(**sessions_stream_args), Views(**views_stream_args)]
