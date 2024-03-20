#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import datetime
import decimal
import functools
import logging
import re
from cgitb import reset
from tracemalloc import start
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from urllib import response

import requests
from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, SyncMode, Type
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.call_rate import APIBudget
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader

from .auth import AdjustAuthenticator, CredentialsCraftAuthenticator
from .model import Report

logger = logging.getLogger("airbyte")

CONFIG_DATE_FORMAT = "%Y-%m-%d"


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
    def supports_incremental(self) -> bool:
        if self.config.get("date_range", {}).get("date_range_type") == "from_date_from_to_today":
            return super().supports_incremental()
        return False

    @property
    def url_base(self) -> str:
        return "https://dash.adjust.com/control-center/reports-service/"

    @property
    def name(self) -> str:
        return self.config["name"]

    @property
    def state(self):
        if self.supports_incremental:
            if self._cursor is not None:
                cursor = self._cursor.isoformat()
            else:
                cursor = self.config["prepared_date_range"]["date_from"].date().isoformat()

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
        fallback = self.config["prepared_date_range"]["date_from"].date()
        cf: str = self.cursor_field

        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            if self.supports_incremental:
                record_stamp = datetime.date.fromisoformat(record[cf])
                self._cursor = max(record_stamp, self._cursor or fallback)
            if self.config.get("rename_fields"):
                for rename_config in self.config["rename_fields"]:
                    try:
                        old, new = rename_config["from"], rename_config["to"]
                        record[new] = record.pop(old)
                    except:
                        pass
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
            model = Report.__dict__["__fields__"].copy()
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
                        self.logger.warning(
                            "Unable to convert field '%s': %s to %s, leaving '%s' as is",
                            k,
                            v,
                            type_.__name__,
                            k,
                        )

            return row

        body = response.json()
        return (reshape(row) for row in body["rows"])

    def stream_slices(
        self, stream_state: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        cf: str = self.cursor_field
        now = datetime.datetime.utcnow().date()
        date_range_type = self.config.get("date_range", {}).get("date_range_type")
        if date_range_type in ["custom_date", "last_n_days"]:
            date = self.config["prepared_date_range"]["date_from"].date()
            end_date = self.config["prepared_date_range"]["date_to"].date()
        elif date_range_type == "from_date_from_to_today":
            if self._cursor and self._cursor > now:
                self.logger.warning(
                    "State ingest target date in future, setting cursor to today's date"
                )
                self._cursor = now
                self.connector.checkpoint()
            if stream_state is not None and stream_state.get(cf):
                date = datetime.date.fromisoformat(stream_state[cf])
                if now - date == datetime.timedelta(days=1):
                    return
            else:
                date = self.config["prepared_date_range"]["date_from"].date()

            if self.config["until_today"]:
                end_date = now
            else:
                end_date = now + datetime.timedelta(days=1)

        while date < end_date:
            yield {cf: date.isoformat()}
            date += datetime.timedelta(days=1)

    @functools.lru_cache(maxsize=None)
    def get_json_schema(self):
        """
        Prune the schema to only include selected fields to synchronize.
        """
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("report")
        properties = schema["properties"]

        required = schema["required"]
        selected = self.config["metrics"] + self.config["dimensions"]
        retain = required + selected
        for attr in list(properties.keys()):
            if attr not in retain:
                del properties[attr]

        for attr in self.config["additional_metrics"]:
            properties[attr] = {"type": "number"}

        if self.config.get("rename_fields"):
            for rename_config in self.config["rename_fields"]:
                old, new = rename_config["from"], rename_config["to"]
                try:
                    properties[new] = properties.pop(old)
                except:
                    pass

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


class Events(HttpStream):
    primary_key = "id"

    def __init__(self, authenticator: AdjustAuthenticator):
        super().__init__(authenticator)

    @property
    def url_base(self) -> str:
        return "https://dash.adjust.com/control-center/reports-service/"

    def path(self, *args, **kwargs) -> str:
        return "events"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from response.json()


class Cohorts(HttpStream):
    primary_key = ["tracker_token", "day"]
    required_config_keys = ["app_id", "cohorts_report_kpis"]

    def __init__(self, authenticator: AdjustAuthenticator, config: Mapping[str, Any]):
        super().__init__(authenticator)
        self.config = config
        self._authenticator = authenticator

    @property
    def url_base(self) -> str:
        return f"https://api.adjust.com/kpis/v1/{self.config.get('app_id')}/"

    def path(self, *args, **kwargs) -> str:
        return "cohorts"

    def next_page_token(self, response: requests.Response) -> Mapping[str, Any]:
        return None

    def get_probe_data(self):
        start_date = self.config["prepared_date_range"]["date_from"].date()
        end_date = start_date + datetime.timedelta(days=1)
        params = self.request_params({}, {}, {})
        params["end_date"] = end_date
        headers = {**self.request_headers({}, {}, {}), **self.authenticator.get_auth_header()}
        r = requests.get(
            url=self.url_base + self.path(),
            headers=headers,
            params=params,
        )
        r.raise_for_status()
        yield from self.parse_response(r, stream_state={}, stream_slice={}, next_page_token={})

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        headers["Accept"] = "text/csv"
        return headers

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        start_date = self.config["prepared_date_range"]["date_from"].date()
        end_date = self.config["prepared_date_range"]["date_to"].date()

        params = {
            "start_date": start_date,
            "end_date": end_date,
            "kpis": ",".join(self.config.get("cohorts_report_kpis")),
            "period": "day",
        }
        if self.config.get("utc_offset"):
            offset = self.config.get("utc_offset")
            offset_marker = "+" if offset >= 0 else "-"
            offset = abs(offset)
            offset_formatted = f"{offset_marker}{offset:02d}:00"
            params["utc_offset"] = offset_formatted
        if self.config.get("cohorts_report_attribution_type"):
            params["attribution_type"] = self.config["cohorts_report_attribution_type"]
        if self.config.get("cohorts_report_attribution_source"):
            params["attribution_source"] = self.config["cohorts_report_attribution_source"]
        if self.config.get("cohorts_report_grouping"):
            params["grouping"] = ",".join(self.config["cohorts_report_grouping"])
        return params

    @functools.lru_cache(maxsize=None)
    def get_json_schema(self):
        """
        Prune the schema to only include selected fields to synchronize.
        """
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("cohorts")
        properties = schema["properties"]
        probe_record = next(self.get_probe_data())
        for attr in probe_record:
            if attr not in self.config["cohorts_report_kpis"]:
                properties[attr] = {"type": ["string", "null"]}
            else:
                properties[attr] = {"type": ["number", "null"]}

        return schema

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        response.encoding = "utf-8-sig"
        resp_data = response.text
        reader = csv.DictReader(resp_data.splitlines())
        for row in reader:
            for key, value in row.items():
                if key in self.config["cohorts_report_kpis"]:
                    try:
                        row[key] = float(value)
                    except ValueError:
                        row[key] = None
            yield row


class EventMetrics(HttpStream):
    primary_key = "id"
    required_config_keys = ["app_id", "event_metrics_report_kpis"]

    def __init__(self, authenticator: AdjustAuthenticator, config: Mapping[str, Any]):
        super().__init__(authenticator)
        self.config = config

    @property
    def url_base(self) -> str:
        return f"https://api.adjust.com/kpis/v1/{self.config.get('app_id')}/"

    def path(self, *args, **kwargs) -> str:
        return "events"

    def next_page_token(self, response: requests.Response) -> Mapping[str, Any]:
        return None

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        headers["Accept"] = "text/csv"
        return headers

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        start_date = self.config["prepared_date_range"]["date_from"].date()
        end_date = self.config["prepared_date_range"]["date_to"].date()
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "kpis": ",".join(self.config.get("event_metrics_report_kpis")),
            "period": "day",
        }
        if self.config.get("utc_offset"):
            offset = self.config.get("utc_offset")
            offset_marker = "+" if offset >= 0 else "-"
            offset = abs(offset)
            offset_formatted = f"{offset_marker}{offset:02d}:00"
            params["utc_offset"] = offset_formatted
        if self.config.get("event_metrics_report_attribution_type"):
            params["attribution_type"] = self.config["event_metrics_report_attribution_type"]
        if self.config.get("event_metrics_report_attribution_source"):
            params["attribution_source"] = self.config["event_metrics_report_attribution_source"]
        if self.config.get("event_metrics_report_grouping"):
            params["grouping"] = ",".join(self.config["event_metrics_report_grouping"])
        return params

    def get_probe_data(self):
        start_date = self.config["prepared_date_range"]["date_from"].date()
        end_date = start_date + datetime.timedelta(days=1)
        params = self.request_params({}, {}, {})
        params["end_date"] = end_date
        headers = {**self.request_headers({}, {}, {}), **self.authenticator.get_auth_header()}
        r = requests.get(
            url=self.url_base + self.path(),
            headers=headers,
            params=params,
        )
        r.raise_for_status()
        r.encoding = "utf-8-sig"
        yield from self.parse_response(r, stream_state={}, stream_slice={}, next_page_token={})

    @functools.lru_cache(maxsize=None)
    def get_json_schema(self):
        """
        Prune the schema to only include selected fields to synchronize.
        """
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("cohorts")
        properties = schema["properties"]

        for attr in self.config["event_metrics_report_kpis"]:
            properties[attr] = {"type": "number"}

        return schema

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        headers["Accept"] = "text/csv"
        return headers

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        response.encoding = "utf-8-sig"
        resp_data = response.text
        reader = csv.DictReader(resp_data.splitlines())
        for row in reader:
            for key, value in row.items():
                if key in self.config["event_metrics_report_kpis"]:
                    try:
                        row[key] = float(value)
                    except ValueError:
                        row[key] = None
            yield row


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
        config = self.prepare_config_datetime(config)
        auth = self.get_authenticator(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            success, message = auth.check_connection()
            if not success:
                return False, message

        for stream in self.streams(config):
            try:
                stream.get_json_schema()
            except Exception as e:
                return False, f"Unable to fetch schema for stream {stream.name}: {e}"

        requests.get(
            url=self.check_endpoint,
            headers=auth.get_auth_header(),
        ).raise_for_status()
        return True, None  # Are we coding in go?

    def get_authenticator(
        self, config: Mapping[str, Any]
    ) -> Union[AdjustAuthenticator, CredentialsCraftAuthenticator]:
        """
        Get authenticator instance.

        :param config: user input configuration as defined in the connector spec.
        """
        auth_type = config["credentials"]["auth_type"]
        if auth_type == "access_token_auth":
            auth = AdjustAuthenticator(token=config["credentials"]["access_token"])
        elif auth_type == "credentials_craft_auth":
            auth = CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception(
                f"Invalid Auth type {auth_type}. Available: access_token_auth and credentials_craft_auth",
            )

        if config.get("account_id"):
            auth.additional_headers = {"X-Account-ID": config["account_id"]}
        return auth

    @staticmethod
    def prepare_config_datetime(config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range = config["date_range"]
        range_type = config["date_range"]["date_range_type"]
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        prepared_range = {}
        if range_type == "custom_date":
            prepared_range["date_from"] = date_range["date_from"]
            prepared_range["date_to"] = date_range["date_to"]
        elif range_type == "from_date_from_to_today":
            prepared_range["date_from"] = date_range["date_from"]
        elif range_type == "last_n_days":
            prepared_range["date_from"] = today - datetime.timedelta(
                days=date_range["last_days_count"]
            )
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - datetime.timedelta(days=1)
        else:
            raise ValueError("Invalid date_range_type")

        if isinstance(prepared_range["date_from"], str):
            prepared_range["date_from"] = datetime.datetime.strptime(
                prepared_range["date_from"], CONFIG_DATE_FORMAT
            )

        if isinstance(prepared_range["date_to"], str):
            prepared_range["date_to"] = datetime.datetime.strptime(
                prepared_range["date_to"], CONFIG_DATE_FORMAT
            )
        config["prepared_date_range"] = prepared_range
        return config

    def streams(self, config: dict[str, Any]) -> List[Stream]:
        """
        Stream registry.

        :param config: user input configuration as defined in the connector spec.
        """
        config = self.prepare_config_datetime(config)
        auth = self.get_authenticator(config)
        self._streams = [Events(authenticator=auth)]

        cohorts_available = True
        for field in Cohorts.required_config_keys:
            if not config.get(field):
                logger.warning(
                    "Cohorts stream is not configured properly, missing %s",
                    field,
                )
                cohorts_available = False
        if cohorts_available:
            self._streams.append(Cohorts(authenticator=auth, config=config))

        event_metrics_available = True
        for field in EventMetrics.required_config_keys:
            if not config.get(field):
                logger.warning(
                    "Event Metrics stream is not configured properly, missing %s",
                    field,
                )
                event_metrics_available = False
        if event_metrics_available:
            self._streams.append(EventMetrics(authenticator=auth, config=config))
        for report_config in config["reports"]:
            report_config: dict[str, Any] = report_config.copy()
            global_config = config.copy()
            global_config.update(report_config)
            del global_config["reports"]
            self._streams.append(
                AdjustReportStream(connector=self, config=global_config, authenticator=auth),
            )
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
