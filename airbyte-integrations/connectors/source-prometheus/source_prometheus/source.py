#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import traceback
from datetime import datetime, timedelta
from abc import ABC
from typing import Any, Dict, Generator, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from base64 import b64encode

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteCatalog,
    AirbyteStream,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources import Source

from prometheus_api_client import PrometheusConnect

from .utils import remove_prefix


class SourcePrometheus(Source):
    def _get_client(self, config: Mapping[str, Any]):
        base_url = config["base_url"]
        basic_auth_user = config["basic_auth_user"]
        basic_auth_pass = config["basic_auth_pass"]

        headers = {}
        if basic_auth_user and basic_auth_pass:
            token = b64encode(f"{basic_auth_user}:{basic_auth_pass}".encode('utf-8')).decode("ascii")
            headers["Authorization"] = f"Basic {token}"

        return PrometheusConnect(url=base_url, headers=headers)

    def _build_stream(self, client: PrometheusConnect, metric: str) -> AirbyteStream:
        labels = list(client.get_label_names(params={'match[]': metric}))
        labels.remove('__name__')

        stream_name = f"metric_{metric}"
        json_schema = json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": [
                {
                    "type": "date-time",
                    "name": "time",
                    "description": "The time of the data point",
                },
                {
                    "type": "number",
                    "name": "value",
                    "description": "The value of the data point",
                },
            ],
        }

        for label in labels:
            json_schema["properties"].append({
                "type": ["string", "null"],
                "name": label,
                "description": f"The value of the label {label}",
            })

        return AirbyteStream(
            name=stream_name,
            json_schema=json_schema,
            supported_sync_modes=["full_refresh", "incremental"],
            sync_mode="full_refresh",
            destination_sync_mode="overwrite",
        )

    def _read_metric(self, client: PrometheusConnect, stream, metric: str, start_date: str, step: int) -> Generator[AirbyteRecordMessage, None, None]:
        cursor = datetime.strptime(start_date, '%Y-%m-%d')

        while True:
            now = datetime.now()
            # Prometheus allows up to 11k data points per response.
            # But since a lot of series can be returned, we limit to 1k data points.
            current_end = cursor + timedelta(seconds=step*1000)
            if current_end > now:
                current_end = now

            data = client.custom_query_range(query=metric, start_time=cursor, end_time=current_end, step=step)
            for serie in data:
                columns = {}
                if 'metric' in serie:
                    columns = serie['metric']
                    del columns['__name__']

                if 'values' in serie:
                    for value in serie['values']:
                        item = {
                            'time': value[0],
                            'value': value[1],
                        }
                        record = columns | item
                        yield AirbyteRecordMessage(stream=stream.name, data=record, emitted_at=int(datetime.now().timestamp()) * 1000)

            cursor = current_end + timedelta(seconds=1)  # end date is inclusive
            if cursor > now:
                break

        # for item in record:
        #     now = int(datetime.now().timestamp()) * 1000
        #     yield AirbyteRecordMessage(stream=stream, data=item, emitted_at=now)

    def check(self, logger, config: Mapping) -> AirbyteConnectionStatus:
        """
        Check involves verifying that the specified file is reachable with
        our credentials.
        """
        try:
            prom = self._get_client(config)
            # prom.get_current_metric_value(metric_name='up')
            if prom.check_prometheus_connection() is False:
                raise Exception("Failed to connect to Prometheus")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            reason = f"Failed to load {config['base_url']}. Please check URL and credentials are set correctly."
            logger.error(f"{reason}\n{repr(err)}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=reason)

    def discover(self, logger: AirbyteLogger, config: Mapping) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in this integration. For example, given valid credentials to a
        Prometheus instance, returns an Airbyte catalog where each metric is a stream, and each column is a label.
        """
        client = self._get_client(config)

        try:
            metrics = client.all_metrics()
            streams = list([self._build_stream(client, metric) for metric in metrics])
            return AirbyteCatalog(streams=streams)
        except Exception as err:
            reason = f"Failed to discover schemas of Prometheus at {config['base_url']}: {repr(err)}\n{traceback.format_exc()}"
            logger.error(reason)
            raise err

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        start_date = config['start_date']
        step = config['step']

        client = self._get_client(config)

        logger.info(f"Starting syncing {self.__class__.__name__}")

        for configured_stream in catalog.streams:
            stream = configured_stream.stream
            logger.info(f"Syncing {stream.name} stream")
            metric_name = remove_prefix(stream.name, "metric_")
            for record in self._read_metric(client, stream, metric_name, start_date, step):
                yield AirbyteMessage(type=Type.RECORD, record=record)

        logger.info(f"Finished syncing {self.__class__.__name__}")
