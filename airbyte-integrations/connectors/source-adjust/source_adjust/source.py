#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import decimal
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import source_adjust.model
from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, SyncMode, Type
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class AdjustReportStream(HttpStream, IncrementalMixin):
    """
    Adjust reports service integration with support for incremental synchronization.
    """

    def __init__(self, connector: "SourceAdjust", config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)

        self.connector = connector
        self.config = config
        self._cursor: Optional[datetime.date] = None

    @property
    def url_base(self) -> str:
        return "https://dash.adjust.com/control-center/reports-service/"

    @property
    def state(self):
        if self._cursor is not None:
            cursor = self._cursor.isoformat()
        else:
            cursor = self.config["ingest_start"]

        return {
            self.cursor_field: cursor,
        }

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._cursor = datetime.date.fromisoformat(value[self.cursor_field])

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        fallback = datetime.date.fromisoformat(self.config["ingest_start"])
        cf: str = self.cursor_field

        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            record_stamp = datetime.date.fromisoformat(record[cf])
            self._cursor = max(record_stamp, self._cursor or fallback)
            yield record

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        """
        Report URL path suffix.
        """
        return "report"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        """
        Get query parameter definitions.
        """
        required_dimensions = ["day"]
        dimensions = required_dimensions + self.config["dimensions"]
        metrics = self.config["metrics"] + self.config["additional_metrics"]
        date = stream_slice[self.cursor_field]
        return {
            "date_period": ":".join([date, date]),  # inclusive
            "metrics": ",".join(metrics),
            "dimensions": ",".join(dimensions),
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        def reshape(row: MutableMapping[str, Any]):
            model = source_adjust.model.Report.__dict__["__fields__"]
            row.pop("attr_dependency", None)
            # Unfortunately all fields are returned as strings by the API
            for k, v in list(row.items()):
                if k in model:
                    type_ = model[k].type_
                else:  # Additional user-provided metrics are assumed to be decimal
                    type_ = decimal.Decimal
                if type_ in (int, decimal.Decimal):
                    try:
                        row[k] = type_(v)
                    except TypeError:
                        self.logger.warning("Unable to convert field '%s': %s to %s, leaving '%s' as is", k, v, type_.__name__, k)

            return row

        body = response.json()
        return (reshape(row) for row in body["rows"])

    def stream_slices(self, stream_state: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        cf: str = self.cursor_field
        now = datetime.datetime.utcnow().date()

        if self._cursor and self._cursor > now:
            self.logger.warning("State ingest target date in future, setting cursor to today's date")
            self._cursor = now
            self.connector.checkpoint()
        if stream_state is not None and stream_state.get(cf):
            date = datetime.date.fromisoformat(stream_state[cf])
            if now - date == datetime.timedelta(days=1):
                return
        else:
            date = datetime.date.fromisoformat(self.config["ingest_start"])

        if self.config["until_today"]:
            end_date = now
        else:
            end_date = now + datetime.timedelta(days=1)

        while date < end_date:
            yield {cf: date.isoformat()}
            date += datetime.timedelta(days=1)

    def get_json_schema(self):
        """
        Prune the schema to only include selected fields to synchronize.
        """
        schema = source_adjust.model.Report.schema()
        properties = schema["properties"]

        required = schema["required"]
        selected = self.config["metrics"] + self.config["dimensions"]
        retain = required + selected
        for attr in list(properties.keys()):
            if attr not in retain:
                del properties[attr]

        for attr in self.config["additional_metrics"]:
            properties[attr] = {"type": "number"}

        return schema

    @property
    def cursor_field(self) -> str:
        """
        Name of the field in the API response body used as cursor.
        """
        return "day"

    @property
    def primary_key(self):
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class SourceAdjust(AbstractSource):
    check_endpoint = "https://dash.adjust.com/control-center/reports-service/filters_data"

    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        """
        Verify the configuration supplied can be used to connect to the API.

        :param config:  config object as per definition in spec.yaml
        :param logger:  logger object
        :return: (True, None) on connecton to the API successfully,
                 (False, error) otherwise.
        """
        requests.get(
            url=self.check_endpoint,
            headers={"Authorization": f'Bearer {config["api_token"]:s}'},
        ).raise_for_status()
        return True, None  # Are we coding in go?

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Stream registry.

        :param config: user input configuration as defined in the connector spec.
        """
        auth = TokenAuthenticator(token=config["api_token"])

        self._streams = [
            AdjustReportStream(connector=self, config=config, authenticator=auth),
        ]
        return self._streams

    def checkpoint(self):
        """
        Checkpoint state.
        """
        state = AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                data={stream.name: stream.state for stream in self._streams},
            ),
        )
        print(state.json(exclude_unset=True))  # Emit state
