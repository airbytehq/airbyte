#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .fields import HitsFields, VisitsFields
from .streams import Evaluate, Sessions, Views, YandexMetricaStream


# Source
class SourceYandexMetrica(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # Check connectivity
            evaluate_views_stream = Evaluate(
                **{
                    "counter_id": config["counter_id"],
                    "params": {
                        "fields": HitsFields.get_all_fields_keys(),
                        "start_date": config["start_date"],
                        "end_date": config["end_date"],
                    },
                    "source": "hits",
                    "authenticator": TokenAuthenticator(token=config["auth_token"]),
                }
            )
            evaluate_sessions_stream = Evaluate(
                **{
                    "counter_id": config["counter_id"],
                    "params": {
                        "fields": VisitsFields.get_all_fields_keys(),
                        "start_date": config["start_date"],
                        "end_date": config["end_date"],
                    },
                    "source": "visits",
                    "authenticator": TokenAuthenticator(token=config["auth_token"]),
                }
            )
            next(evaluate_views_stream.read_records(sync_mode=SyncMode.full_refresh))
            next(evaluate_sessions_stream.read_records(sync_mode=SyncMode.full_refresh))

            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[YandexMetricaStream]:
        authenticator = TokenAuthenticator(token=config["auth_token"])
        views_stream_args = {
            "counter_id": config["counter_id"],
            "params": {
                "fields": HitsFields.get_all_fields_keys(),
                "start_date": config["start_date"],
                "end_date": config["end_date"],
            },
            "authenticator": authenticator,
        }
        sessions_stream_args = {
            "counter_id": config["counter_id"],
            "params": {
                "fields": VisitsFields.get_all_fields_keys(),
                "start_date": config["start_date"],
                "end_date": config["end_date"],
            },
            "authenticator": authenticator,
        }
        return [Sessions(**sessions_stream_args), Views(**views_stream_args)]
