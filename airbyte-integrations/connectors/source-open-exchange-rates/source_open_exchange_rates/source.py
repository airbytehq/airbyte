#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, MutableMapping, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream


# TODO: remove when overriding _read_incremental() is no longer required
from typing import Iterator, MutableMapping
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteMessage,
    ConfiguredAirbyteStream,
    SyncMode
)
################

from source_open_exchange_rates.streams import HistoricalExchangeRates


class SourceOpenExchangeRates(AbstractSource):
    """
    Source dedicated to synchronise entities (i.e. nodes and relationships) of a Neo4j database
    """
    @property
    def logger(self) -> AirbyteLogger:
        """
        Get logger
        :return: AirbyteLogger
        """
        return AirbyteLogger()


    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            params = {"app_id": config["app_id"]}
            base = config.get("base")
            if base is not None:
                params["base"] = base

            resp = requests.get(f"{HistoricalExchangeRates.url_base}{config['start_date']}.json", params=params)
            status = resp.status_code
            logger.info(f"Ping response code: {status}")
            if status == 200:
                return True, None
            # When API requests is sent but the requested data is not available or the API call fails
            # for some reason, a JSON error is returned.
            # https://docs.openexchangerates.org/v0.7/docs/errors
            error = resp.json()
            status = error.get("status")
            message = error.get("message")
            description = error.get("description")

            return False, f"Error {status} - {message}: {description}"
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams = [
            HistoricalExchangeRates(
                app_id=config["app_id"],
                start_date=config["start_date"],
                base=config.get("base"),
                symbols=config.get("symbols"),
                show_alternative=config.get("show_alternative", False),
                prettyprint=config.get("prettyprint", False),
                ignore_current_day=config.get("ignore_current_day", True),
                ignore_weekends=config.get("ignore_weekends", False),
                max_records_per_sync=config.get("max_records_per_sync")
            )
        ]
        return streams
