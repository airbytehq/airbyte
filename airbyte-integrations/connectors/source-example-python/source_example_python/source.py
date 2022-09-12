#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import sys
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Generator

import requests

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import Source


class SourceExamplePython(Source):

    @staticmethod
    def _call_api(ticker, token, from_day, to_day):
        return requests.get(
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{from_day}/{to_day}?sort=asc&limit=120&apiKey={token}")

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        try:
            today = datetime.today()
            to_day = today.strftime("%Y-%m-%d")
            from_day = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            response = self._call_api(ticker=config["stock_ticker"], token=config["api_key"],
                                      from_day=from_day, to_day=to_day)
            if response.status_code == 200:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            elif response.status_code == 403:
                # HTTP code 403 means authorization failed so the API key is incorrect
                result = {"status": "FAILED", "message": "API Key is incorrect."}
                raise Exception(result)
            raise Exception('Unknown Error')

        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        streams = []
        catalog = {
            "streams": [
                {
                    "stream": {
                        "name": "stock_prices",
                        "supported_sync_modes": [
                            "full_refresh",
                            "incremental"
                        ],
                        "json_schema": {
                            "properties": {
                                "date": {
                                    "type": "string"
                                },
                                "price": {
                                    "type": "number"
                                },
                                "stock_ticker": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                }
            ]
        }

        for configured_stream in catalog.get('streams'):
            stream = configured_stream.get('stream')
            streams.append(AirbyteStream(name=stream.get('name'), json_schema=stream.get('json_schema'),
                                         supported_sync_modes=stream.get('supported_sync_modes')))
        return AirbyteCatalog(streams=streams)

    def read(self,
             logger: AirbyteLogger,
             config: json,
             catalog: ConfiguredAirbyteCatalog,
             state: Dict[str, any]) -> Generator[AirbyteMessage, None, None]:
        stream_name = "stock_prices"  # Example

        if "api_key" not in config or "stock_ticker" not in config:
            logger.info("Input config must contain the properties 'api_key' and 'stock_ticker'")
            sys.exit(1)

        stock_prices_stream = None
        for configured_stream in catalog.streams:
            if configured_stream.stream.name == "stock_prices":
                stock_prices_stream = configured_stream

        if stock_prices_stream is None:
            logger.info("No streams selected")
            return

        today = date.today()
        cursor_value = today.strftime("%Y-%m-%d")
        from_day = (today - timedelta(days=7)).strftime("%Y-%m-%d")

        # In case of incremental sync, state should contain the last date when we fetched stock prices
        if stock_prices_stream.sync_mode == SyncMode.incremental:
            if state and "stock_prices" in state and state["stock_prices"].get("date"):
                from_date = datetime.strptime(state["stock_prices"].get("date"), "%Y-%m-%d")
                from_day = (from_date + timedelta(days=1)).strftime("%Y-%m-%d")

        # If the state indicates that we have already ran the sync up to cursor_value, we can skip the sync
        if cursor_value > from_day:
            # If we've made it this far, all the configuration is good and we can pull the market data
            response = self._call_api(ticker=config["stock_ticker"], token=config["api_key"], from_day=from_day, to_day=cursor_value)
            if response.status_code != 200:
                # In a real scenario we'd handle this error better :)
                logger.info(f"Failure occurred when calling Polygon.io API, {response.status_code=}, {response.text=}")
                sys.exit(1)
            else:
                # Stock prices are returned sorted by date in ascending order
                # We want to output them one by one as AirbyteMessages
                response_json = response.json()
                if response_json["resultsCount"] > 0:
                    results = response_json["results"]
                    for result in results:
                        data = {"date": datetime.fromtimestamp(result["t"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d"),
                                "stock_ticker": config["stock_ticker"], "price": result["c"]}

                        yield AirbyteMessage(
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                        )

                        if stock_prices_stream.sync_mode == "incremental":
                            cursor_value = datetime.fromtimestamp(results[len(results) - 1]["t"] / 1000, tz=timezone.utc).strftime(
                                "%Y-%m-%d")

        if stock_prices_stream.sync_mode == SyncMode.incremental:
            yield AirbyteMessage(
                type=Type.STATE,
                state=AirbyteStateMessage(data={"stock_prices": {"date": cursor_value}}))
