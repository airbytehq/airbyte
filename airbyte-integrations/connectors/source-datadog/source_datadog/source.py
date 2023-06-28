#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import Any, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from pydantic.datetime_parse import timedelta
from source_datadog.streams import (
    AuditLogs,
    Dashboards,
    Downtimes,
    Incidents,
    IncidentTeams,
    Logs,
    Metrics,
    SeriesStream,
    SyntheticTests,
    Users,
)


class SourceDatadog(AbstractSource):
    @staticmethod
    def _get_authenticator(config: Mapping[str, Any]):
        return DatadogAuthenticator(api_key=config["api_key"], application_key=config["application_key"])

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            args = self.connector_config(config)
            dashboards_stream = Dashboards(**args)
            records = dashboards_stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records, None)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = self.connector_config(config)
        base_streams = [
            AuditLogs(**args),
            Dashboards(**args),
            Downtimes(**args),
            Incidents(**args),
            IncidentTeams(**args),
            Logs(**args),
            Metrics(**args),
            SyntheticTests(**args),
            Users(**args),
        ]
        queries = config.get("queries", [])

        # Create a stream for each query in the list
        query_streams = []
        for query in queries:
            if all(field in query and query[field] for field in ["name", "data_source", "query"]):
                name = query["name"]
                data_source = query["data_source"]
                query_string = query["query"]

                # Create a new stream using the query name, data source, and query string
                new_stream = SeriesStream(
                    name=name,
                    data_source=data_source,
                    query_string=query_string,
                    **args,
                )
                query_streams.append(new_stream)
            else:
                logging.info("Query fields are missing, Streams not created")

        # Combine the base streams and query streams
        return base_streams + query_streams

    def connector_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "site": config.get("site", "datadoghq.com"),
            "authenticator": self._get_authenticator(config),
            "query": config.get("query", ""),
            "max_records_per_request": config.get("max_records_per_request", 5000),
            "start_date": config.get("start_date", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")),
            "end_date": config.get("end_date", (datetime.now() + timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")),
            "query_start_date": config.get("start_date", ""),
            "query_end_date": config.get("end_date", ""),
            "queries": config.get("queries", []),
        }


class DatadogAuthenticator(requests.auth.AuthBase):
    def __init__(self, api_key: str, application_key: str):
        self.api_key = api_key
        self.application_key = application_key

    def __call__(self, r):
        r.headers["DD-API-KEY"] = self.api_key
        r.headers["DD-APPLICATION-KEY"] = self.application_key
        return r
