#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import StreamData

import requests
import hashlib
import hmac
import json
import uuid
import base64
import pendulum
import logging
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream


logger = logging.getLogger("airbyte")

BASE_URL = "https://prod.api.fiservapps.com/"


class FiservStream(HttpStream, ABC):
    url_base = BASE_URL
    endpoint = None

    def __init__(
        self, *args, start_date: str = None, api_key: str = None, api_secret: str = None, fields: Optional[List[str]] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        if isinstance(start_date, str):
            start_date = pendulum.parse(start_date)

        self._start_date = start_date.strftime("%Y%m%d")
        self.end_date = pendulum.yesterday(tz="utc").strftime("%Y%m%d")

        self._api_secret = api_secret
        self._api_key = api_key
        self._fields = fields

    @property
    def http_method(self) -> str:
        return "POST"

    def _chunk_date_range(self, start_date: str, end_date: str) -> Iterable[Mapping[str, str]]:
        start_date = pendulum.parse(start_date)
        end_date = pendulum.parse(end_date)
        chunk_start_date = start_date
        while chunk_start_date < end_date:
            chunck_end_date = chunk_start_date.add(days=1)
            yield {"fromDate": chunk_start_date.strftime("%Y%m%d"), "toDate": chunck_end_date.strftime("%Y%m%d")}
            chunk_start_date = chunck_end_date

    def _generate_hmac(self, request_id: str, ts: str, body: Mapping[str, Any]):
        body = json.dumps(body)
        msg = f"{self._api_key}{request_id}{ts}{body}"
        hashed = hmac.new(
            bytes(self._api_secret, "utf-8"),
            bytes(msg, "utf-8"),
            hashlib.sha256,
        )
        return base64.b64encode(hashed.digest()).decode()

    def request_body_json(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        body = stream_slice if stream_slice else {}
        if self._fields:
            body["fields"] = self._fields

        return body

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        request_id = str(uuid.uuid4())
        ts = str(int(pendulum.now(tz="UTC").timestamp() * 1000))
        body = self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        hmac_signature = self._generate_hmac(request_id, ts, body)
        return {
            "Content-Type": "application/json",
            "Api-Key": self._api_key,
            "Client-Request-Id": request_id,
            "Timestamp": ts,
            "Auth-Token-Type": "HMAC",
            "Authorization": hmac_signature,
        }

    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"reporting/v1/{self.endpoint}/search"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Mapping[str, str]]:
        stream_state = stream_state or {}
        start_date = self._start_date

        if cursor_field:
            field = cursor_field[0]
            start_date = stream_state.get(field, self._start_date)

        yield from self._chunk_date_range(start_date, self.end_date)

    @property
    def availability_strategy(self):
        return None


class IncrementalFiservStream(FiservStream, IncrementalMixin):
    cursor_field = "last_sync_at"
    _cursor_value = None

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value or self._start_date}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field) or self._start_date

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:
        stream_slice = stream_slice or {}
        records = super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

        old_cursor = self._cursor_value or self._start_date
        new_cursor = stream_slice.get("toDate", self.end_date)

        for record in records:
            record[self.cursor_field] = new_cursor
            yield record

        self._cursor_value = max(new_cursor, old_cursor)


class Settlement(IncrementalFiservStream):
    primary_key = "visaTranId"
    endpoint = "settlement"


class Chargeback(IncrementalFiservStream):
    primary_key = "chargebackReferenceId"  # represents the last date data was fetched
    endpoint = "chargeback"


class Disbursement(IncrementalFiservStream):
    primary_key = "paymentVendorId"
    endpoint = "disbursement"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        body = super().request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        return {**body, "filters": {"dateType": "PaymentDate", "currency": "USD", "timeZone": "UTC"}}


class Funding(IncrementalFiservStream):
    primary_key = "siteID"
    endpoint = "funding"


class Commercehub(IncrementalFiservStream):
    primary_key = "clientRequestID"
    endpoint = "commercehub"


class Retrieval(IncrementalFiservStream):
    primary_key = "debitNetworkIDKey"
    endpoint = "retrieval"

class Authorization(IncrementalFiservStream):
    primary_key = "externalTerminalID"
    endpoint = "authorization"


class Sites(FiservStream):
    primary_key = "corpID"
    endpoint = "reference/sites"

    def request_body_json(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping[str, Any]]:
        return {"filters": {}}

    def stream_slices(self, sync_mode, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[MutableMapping[str, any]]]:
        return [None]


class Transactions(IncrementalFiservStream):
    primary_key = "nrtmConsortiumID"
    endpoint = "prepaid/transactions"


class Bin(FiservStream):
    primary_key = "id"
    endpoint = "reference/bins"

    parent_streams = [(Chargeback, "First6", "first6"), (Retrieval, "First6", "first6"), (Settlement, "First6", "first6")]

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        logger.info("Requesting stream slices")
        all_bin_ids = set()
        for ParentStream, filter_field, target_field in self.parent_streams:
            kwargs = {
                "api_key": self._api_key,
                "api_secret": self._api_secret,
                "start_date": self._start_date,
                "fields": [filter_field],
            }

            parent_stream_instance = ParentStream(**kwargs)
            logger.info("========================")
            logger.info(f"Processing {parent_stream_instance.name} from {self._start_date}")

            for stream_slice in parent_stream_instance.stream_slices(sync_mode=SyncMode.full_refresh):
                for record in parent_stream_instance.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                    bin_ids = record.get(target_field)
                    if bin_ids:
                        all_bin_ids.add(bin_ids)

        logger.info("Done processing bin parent streams")
        logger.info("===========================")
        logger.info(all_bin_ids)
        for bin_id in all_bin_ids:
            yield {"bin_id": bin_id}

    def request_body_json(  # log request json
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:
        bin_id = stream_slice.get("bin_id")
        return {"filters": {"bin": bin_id}}


class SourceFiserv(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        kwargs = {
            "api_key": config.get("api_key"),
            "api_secret": config.get("api_secret"),
            "start_date": pendulum.now(tz="UTC").date().subtract(days=2),
        }

        sites = Sites(**kwargs).read_records(
            sync_mode=SyncMode.full_refresh,
        )
        next(sites)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        kwargs = {
            "api_key": config.get("api_key"),
            "api_secret": config.get("api_secret"),
            "start_date": config.get("start_date"),
        }

        return [
            Chargeback(**kwargs),
            Disbursement(**kwargs),
            Funding(**kwargs),
            Commercehub(**kwargs),
            Retrieval(**kwargs),
            Settlement(**kwargs),
            Bin(**kwargs),
            Sites(**kwargs),
            Authorization(**kwargs),
            Transactions(**kwargs),
        ]
