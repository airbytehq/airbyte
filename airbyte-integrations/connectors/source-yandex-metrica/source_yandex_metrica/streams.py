#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import csv
import io
import re
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream

from .enums import YMCursor, YMPrimaryKey, YMSource, YMStatus
from .fields import HitsFields, VisitsFields

STATE_CHECKPOINT_INTERVAL = 20

# Full refresh streams


class YandexMetricaStream(HttpStream, ABC):
    url_base = "https://api-metrica.yandex.net/management/v1/counter/"

    @property
    def primary_key(self):
        return YMPrimaryKey.VIEWS if self.params["source"] == YMSource.VIEWS else YMPrimaryKey.SESSIONS

    @property
    def cursor_field(self) -> str:
        return YMCursor.VIEWS if self.params["source"] == YMSource.VIEWS else YMCursor.SESSIONS

    def __init__(self, counter_id: str, params: dict, **kwargs):
        self.counter_id = counter_id
        self.params = params
        super().__init__(**kwargs)

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Content-Type": "application/x-ymetrika+json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def fetch_records(self, response: requests.Response, stream_state: Mapping[str, Any] = {}) -> Iterable[Mapping]:
        try:
            # Configure state
            self.params["start_date"] = stream_state.get("start_date", self.params["start_date"])
            self.params["end_date"] = stream_state.get("end_date", self.params["end_date"])
            # 1. Evaluate a logrequest is valid
            evaluate = Evaluate(
                authenticator=self._authenticator, counter_id=self.counter_id, params=self.params, source=self.params["source"]
            )
            evaluate_response = next(evaluate.read_records(sync_mode=SyncMode.full_refresh))
            if not evaluate_response["log_request_evaluation"]["possible"]:
                yield {}
            # 2. Create logrequest
            create = Create(authenticator=self._authenticator, counter_id=self.counter_id, params=self.params)
            create_response = next(create.read_records(sync_mode=SyncMode.full_refresh))
            logrequest_id = create_response["log_request"]["request_id"]
            if not logrequest_id:
                yield {}
            # 3. Check logrequest status
            check = Check(authenticator=self._authenticator, counter_id=self.counter_id, params=self.params, logrequest_id=logrequest_id)
            check_response = next(check.read_records(sync_mode=SyncMode.full_refresh))
            if not check_response:
                yield {}
            last_page = check_response["log_request"]["parts"][-1]["part_number"]
            # 4. Download the logs
            download = Download(
                authenticator=self._authenticator,
                counter_id=self.counter_id,
                params=self.params,
                logrequest_id=logrequest_id,
                last_page=last_page,
            )
            download_response = download.read_records(sync_mode=SyncMode.full_refresh)

            yield from download_response
            # 5. Clean logrequest
            clean = Clean(
                authenticator=self._authenticator,
                counter_id=self.counter_id,
                params=self.params,
                logrequest_id=logrequest_id,
            )
            next(clean.read_records(sync_mode=SyncMode.full_refresh))
        except Exception as e:
            print(f"Exception occurred while trying to fetch records: {e}")


# Incremental streams
class IncrementalYandexMetricaStream(YandexMetricaStream, IncrementalMixin):
    state_checkpoint_interval = STATE_CHECKPOINT_INTERVAL

    def __init__(self, counter_id: str, params: dict, **kwargs):
        super().__init__(counter_id, params, **kwargs)
        self._cursor_value = ""

    @property  # State getter
    def state(self) -> MutableMapping[str, Any]:
        return (
            {self.cursor_field: self._cursor_value, "start_date": self._start_date, "end_date": self._end_date}
            if self._cursor_value
            else {}
        )

    @state.setter  # State setter
    def state(self, value: MutableMapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field, "1970-01-01T00:00:00")
        self._start_date = value.get("start_date", self.params["start_date"])
        self._end_date = value.get("end_date", self.params["end_date"])

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return {
            "date1": stream_state.get("start_date", self.params["start_date"]),
            "date2": stream_state.get("end_date", self.params["end_date"]),
            "source": self.params["source"],
            "fields": self.params["fields"],
        }

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            yield record
            self._cursor_value = max(record[self.cursor_field], self._cursor_value)

        self._start_date = self.params["end_date"]
        self._end_date = datetime.strftime(datetime.now() - timedelta(1), "%Y-%m-%d")


class Views(IncrementalYandexMetricaStream):
    def __init__(self, counter_id: str, params: dict, **kwargs):
        self.fields_list = params["fields"]
        fields = ",".join(params["fields"])
        params["source"] = YMSource.VIEWS
        params["fields"] = fields
        super().__init__(counter_id, params, **kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.counter_id}/logrequests/evaluate"

    def get_json_schema(self) -> Mapping[str, any]:
        schema = super().get_json_schema()
        schema = {"$schema": "http://json-schema.org/draft-04/schema#", "type": "object", "properties": {}}
        fields = {key: HitsFields.get_all_fields()[key] for key in self.fields_list}
        for key, value in fields.items():
            key = re.sub(r"(ym:s:|ym:pv:)", "", key)
            schema["properties"][key] = value

        return schema

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state=stream_state)

    @property
    def raise_on_http_errors(self) -> bool:
        return False

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        yield from self.fetch_records(response, stream_state)


class Sessions(IncrementalYandexMetricaStream):
    def __init__(self, counter_id: str, params: dict, **kwargs):
        self.fields_list = params["fields"]
        fields = ",".join(params["fields"])
        params["source"] = YMSource.SESSIONS
        params["fields"] = fields
        super().__init__(counter_id, params, **kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.counter_id}/logrequests/evaluate"

    def get_json_schema(self) -> Mapping[str, any]:
        schema = super().get_json_schema()
        schema = {"$schema": "http://json-schema.org/draft-04/schema#", "type": "object", "properties": {}}
        fields = {key: VisitsFields.get_all_fields()[key] for key in self.fields_list}
        for key, value in fields.items():
            key = re.sub(r"(ym:s:|ym:pv:)", "", key)
            schema["properties"][key] = value

        return schema

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state=stream_state)

    @property
    def raise_on_http_errors(self) -> bool:
        return False

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        yield from self.fetch_records(response, stream_state)


# Substreams
"""
Evaluates the possibility of creating a logs request according to its approximate size.

See: https://yandex.com/dev/metrika/doc/api2/logs/queries/evaluate.html
"""


class Evaluate(YandexMetricaStream):
    primary_key = None

    def __init__(self, counter_id: str, params: dict, source: str, **kwargs):
        super().__init__(counter_id, params, **kwargs)
        self.params = params
        self.params["source"] = source

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.counter_id}/logrequests/evaluate"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "date1": self.params["start_date"],
            "date2": self.params["end_date"],
            "source": self.params["source"],
            "fields": self.params["fields"],
        }

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        data = response.json()
        yield data


"""
Creates logs request.

See: https://yandex.com/dev/metrika/doc/api2/logs/queries/createlogrequest.html
"""


class Create(YandexMetricaStream):
    primary_key = None

    def __init__(self, counter_id: str, params: dict, **kwargs):
        super().__init__(counter_id, params, **kwargs)

    @property
    def http_method(self) -> str:
        return "POST"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.counter_id}/logrequests"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "date1": self.params["start_date"],
            "date2": self.params["end_date"],
            "source": self.params["source"],
            "fields": self.params["fields"],
        }

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        data = response.json()
        yield data


"""
Returns information about logs request.

See: https://yandex.com/dev/metrika/doc/api2/logs/queries/getlogrequest.html
"""


class Check(YandexMetricaStream):
    primary_key = None

    def __init__(self, counter_id: str, params: dict, logrequest_id: int, **kwargs):
        self.logrequest_id = logrequest_id
        super().__init__(counter_id, params, **kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.counter_id}/logrequest/{self.logrequest_id}"

    @property
    def max_retries(self) -> Union[int, None]:
        return 240

    def should_retry(self, response: requests.Response) -> bool:
        data = response.json()
        return data["log_request"]["status"] != YMStatus.PROCESSED

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        return 30

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        data = response.json()
        yield data


"""
Download prepared logs of the processed request.

See: https://yandex.com/dev/metrika/doc/api2/logs/queries/download.html
"""


class Download(YandexMetricaStream):
    def __init__(self, counter_id: str, params: dict, logrequest_id: int, last_page: int, **kwargs):
        self.logrequest_id = logrequest_id
        self.last_page = last_page
        self.first_page = True
        super().__init__(counter_id, params, **kwargs)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        self.first_page = False
        current_page = int(response.url.split("/")[-2])
        if current_page < self.last_page:
            return {"page_number": current_page + 1}
        return None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.first_page:
            return f"{self.counter_id}/logrequest/{self.logrequest_id}/part/0/download"

        return f"{self.counter_id}/logrequest/{self.logrequest_id}/part/{next_page_token['page_number']}/download"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        reader = csv.DictReader(io.StringIO(response.text), delimiter="\t")
        for row in reader:
            # Remove 'ym:s:' or 'ym:pv:' prefix
            row = {re.sub(r"(ym:s:|ym:pv:)", "", key): value for key, value in row.items()}
            try:
                # Transform datetime fields
                row[self.cursor_field] = row[self.cursor_field].replace(" ", "T")
            except Exception as e:
                print(f"Something went wrong while transforming datetime fields. {e}")

            yield row


"""
Clears logs of the processed request prepared for downloading.

See: https://yandex.com/dev/metrika/doc/api2/logs/queries/clean.html
"""


class Clean(YandexMetricaStream):
    primary_key = None

    def __init__(self, counter_id: str, logrequest_id: int, params: dict, **kwargs):
        self.counter_id = counter_id
        self.logrequest_id = logrequest_id
        super().__init__(counter_id, params, **kwargs)

    @property
    def http_method(self) -> str:
        return "POST"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.counter_id}/logrequest/{self.logrequest_id}/clean"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        data = response.json()
        return data
