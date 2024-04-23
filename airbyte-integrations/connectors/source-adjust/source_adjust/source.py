#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import decimal
import functools
import logging
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader

from .auth import AdjustAuthenticator, CredentialsCraftAuthenticator
from .model import Report

logger = logging.getLogger("airbyte")

CONFIG_DATE_FORMAT = "%Y-%m-%d"


class AdjustReportStream(HttpStream, IncrementalMixin):
    """
    Adjust reports service integration with support for incremental synchronization.
    """

    def __init__(
        self,
        name: str,
        prepared_date_range: dict[str, any],
        date_range: dict[str, any],
        dimensions: list[str],
        metrics: list[str],
        additional_metrics: Optional[list[str]] = None,
        adjust_account_id: Optional[int] = None,
        field_name_map: Optional[dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._cursor: Optional[datetime.date] = None

        self._name: str = name
        self._date_range: dict[str, any] = date_range
        self._prepared_date_range: dict[str, any] = prepared_date_range
        self._adjust_account_id: Optional[int] = adjust_account_id
        self._field_name_map: dict[str, str] = field_name_map if field_name_map is not None else {}

        self._dimensions: list[str] = dimensions
        self._metrics: list[str] = metrics
        self._additional_metrics: list[str] = additional_metrics if additional_metrics is not None else []

    @property
    def supports_incremental(self) -> bool:
        if self._date_range.get("date_range_type") == "from_date_from_to_today":
            return super().supports_incremental
        return False

    @property
    def url_base(self) -> str:
        return "https://dash.adjust.com/control-center/reports-service/"

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self):
        if self.supports_incremental:
            if self._cursor is not None:
                cursor = self._cursor.isoformat()
            else:
                cursor = self._prepared_date_range["date_from"].date().isoformat()

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
        fallback = self._prepared_date_range["date_from"].date()
        cf: str = self.cursor_field

        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            if self.supports_incremental:
                record_stamp = datetime.date.fromisoformat(record[cf])
                self._cursor = max(record_stamp, self._cursor or fallback)

            for old_name, new_name in self._field_name_map.items():
                if old_name in record:
                    record[new_name] = record.pop(old_name)
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
        dimensions = required_dimensions + self._dimensions
        metrics = self._metrics + self._additional_metrics
        date = stream_slice[self.cursor_field]
        params = {
            "date_period": ":".join([date, date]),  # inclusive
            "metrics": ",".join(metrics),
            "dimensions": ",".join(dimensions),
        }

        if self._adjust_account_id is not None:
            params["adjust_account_id"] = self._adjust_account_id

        return params

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

    def stream_slices(self, stream_state: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        cf: str = self.cursor_field
        now = datetime.datetime.utcnow().date()
        date_range_type = self._date_range.get("date_range_type")
        if date_range_type in ["custom_date", "last_n_days"]:
            date = self._prepared_date_range["date_from"].date()
            end_date = self._prepared_date_range["date_to"].date()
        elif date_range_type == "from_date_from_to_today":
            if self._cursor and self._cursor > now:
                self.logger.warning("State ingest target date in future, setting cursor to today's date")
                self._cursor = now
            if stream_state is not None and stream_state.get(cf):
                date = datetime.date.fromisoformat(stream_state[cf])
                if now - date == datetime.timedelta(days=1):
                    return
            else:
                self._prepared_date_range["date_from"].date()

            # if not self._date_range["load_today"]:
            #     end_date = now
            # else:
            #     end_date = now + datetime.timedelta(days=1)

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
        selected = self._metrics + self._dimensions
        retain = required + selected
        for attr in list(properties.keys()):
            if attr not in retain:
                del properties[attr]

        for attr in self._additional_metrics:
            properties[attr] = {"type": "number"}

        for old_val, new_val in self._field_name_map.items():
            if old_val in properties:
                properties[new_val] = properties.pop(old_val)

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

    def get_authenticator(self, config: Mapping[str, Any]) -> Union[AdjustAuthenticator, CredentialsCraftAuthenticator]:
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
            prepared_range["date_from"] = today - datetime.timedelta(days=date_range["last_days_count"])
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - datetime.timedelta(days=1)
        else:
            raise ValueError("Invalid date_range_type")

        if isinstance(prepared_range["date_from"], str):
            prepared_range["date_from"] = datetime.datetime.strptime(prepared_range["date_from"], CONFIG_DATE_FORMAT)

        if isinstance(prepared_range["date_to"], str):
            prepared_range["date_to"] = datetime.datetime.strptime(prepared_range["date_to"], CONFIG_DATE_FORMAT)
        config["prepared_date_range"] = prepared_range
        return config

    @staticmethod
    def get_field_name_map(config: Mapping[str, any]) -> dict[str, str]:
        """Get values that needs to be replaced and their replacements"""
        field_name_map: Optional[list[dict[str, str]]]
        if not (field_name_map := config.get("field_name_map")):
            return {}
        else:
            return {item["old_value"]: item["new_value"] for item in field_name_map}

    @staticmethod
    def prepare_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        config = SourceAdjust.prepare_config_datetime(config)
        for report in config["reports"]:
            report["field_name_map"] = SourceAdjust.get_field_name_map(report)
        return config

    def streams(self, config: dict[str, Any]) -> List[Stream]:
        """
        Stream registry.

        :param config: user input configuration as defined in the connector spec.
        """
        config = self.prepare_config(config)
        auth = self.get_authenticator(config)

        streams = [Events(authenticator=auth)]

        for report_config in config["reports"]:
            streams.append(
                AdjustReportStream(
                    name=report_config["name"],
                    prepared_date_range=config["prepared_date_range"].copy(),
                    date_range=config["date_range"].copy(),
                    dimensions=report_config["dimensions"],
                    metrics=report_config["metrics"],
                    additional_metrics=report_config["additional_metrics"],
                    field_name_map=config.get("field_name_map"),
                    adjust_account_id=config.get("account_id"),
                    authenticator=auth,
                ),
            )
        return streams
