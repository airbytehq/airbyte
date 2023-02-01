#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from functools import partial
from queue import Queue
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from cached_property import cached_property
from facebook_business.adobjects.abstractobject import AbstractObject
from facebook_business.api import FacebookAdsApiBatch, FacebookRequest, FacebookResponse

from .common import deep_merge

if TYPE_CHECKING:  # pragma: no cover
    from source_facebook_marketing.api import API

logger = logging.getLogger("airbyte")

FACEBOOK_BATCH_ERROR_CODE = 960


class FBMarketingStream(Stream, ABC):
    """Base stream class"""

    primary_key = "id"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    # use batch API to retrieve details for each record in a stream
    use_batch = True
    # this flag will override `include_deleted` option for streams that does not support it
    enable_deleted = True
    # entity prefix for `include_deleted` filter, it usually matches singular version of stream name
    entity_prefix = None

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def __init__(self, api: "API", include_deleted: bool = False, page_size: int = 100, max_batch_size: int = 50, **kwargs):
        super().__init__(**kwargs)
        self._api = api
        self.page_size = page_size if page_size is not None else 100
        self._include_deleted = include_deleted if self.enable_deleted else False
        self.max_batch_size = max_batch_size if max_batch_size is not None else 50

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        return list(self.get_json_schema().get("properties", {}).keys())

    def _execute_batch(self, batch: FacebookAdsApiBatch) -> None:
        """Execute batch, retry in case of failures"""
        while batch:
            batch = batch.execute()
            if batch:
                logger.info("Retry failed requests in batch")

    def execute_in_batch(self, pending_requests: Iterable[FacebookRequest]) -> Iterable[MutableMapping[str, Any]]:
        """Execute list of requests in batches"""
        requests_q = Queue()
        records = []
        for r in pending_requests:
            requests_q.put(r)

        def success(response: FacebookResponse):
            records.append(response.json())

        def failure(response: FacebookResponse, request: Optional[FacebookRequest] = None):
            # although it is Optional in the signature for compatibility, we need it always
            assert request, "Missing a request object"
            resp_body = response.json()
            if not isinstance(resp_body, dict) or resp_body.get("error", {}).get("code") != FACEBOOK_BATCH_ERROR_CODE:
                # response body is not a json object or the error code is different
                raise RuntimeError(f"Batch request failed with response: {resp_body}")
            requests_q.put(request)

        api_batch: FacebookAdsApiBatch = self._api.api.new_batch()

        while not requests_q.empty():
            request = requests_q.get()
            api_batch.add_request(request, success=success, failure=partial(failure, request=request))
            if len(api_batch) == self.max_batch_size or requests_q.empty():
                # make a call for every max_batch_size items or less if it is the last call
                self._execute_batch(api_batch)
                yield from records
                records = []
                api_batch: FacebookAdsApiBatch = self._api.api.new_batch()

        yield from records

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Main read method used by CDK"""
        records_iter = self.list_objects(params=self.request_params(stream_state=stream_state))
        loaded_records_iter = (record.api_get(fields=self.fields, pending=self.use_batch) for record in records_iter)
        if self.use_batch:
            loaded_records_iter = self.execute_in_batch(loaded_records_iter)

        for record in loaded_records_iter:
            if isinstance(record, AbstractObject):
                yield record.export_all_data()  # convert FB object to dict
            else:
                yield record  # execute_in_batch will emmit dicts

    @abstractmethod
    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        """List FB objects, these objects will be loaded in read_records later with their details.

        :param params: params to make request
        :return: list of FB objects to load
        """

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        """Parameters that should be passed to query_records method"""
        params = {"limit": self.page_size}

        if self._include_deleted:
            params.update(self._filter_all_statuses())

        return params

    def _filter_all_statuses(self) -> MutableMapping[str, Any]:
        """Filter that covers all possible statuses thus including deleted/archived records"""
        filt_values = [
            "active",
            "archived",
            "completed",
            "limited",
            "not_delivering",
            "deleted",
            "not_published",
            "pending_review",
            "permanently_deleted",
            "recently_completed",
            "recently_rejected",
            "rejected",
            "scheduled",
            "inactive",
        ]

        return {
            "filtering": [
                {"field": f"{self.entity_prefix}.delivery_info", "operator": "IN", "value": filt_values},
            ],
        }


class FBMarketingIncrementalStream(FBMarketingStream, ABC):
    """Base class for incremental streams"""

    cursor_field = "updated_time"

    def __init__(self, start_date: datetime, end_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.instance(start_date)
        self._end_date = pendulum.instance(end_date)

        if self._end_date < self._start_date:
            logger.error("The end_date must be after start_date.")

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """Update stream state from latest record"""
        potentially_new_records_in_the_past = self._include_deleted and not current_stream_state.get("include_deleted", False)
        record_value = latest_record[self.cursor_field]
        state_value = current_stream_state.get(self.cursor_field) or record_value
        max_cursor = max(pendulum.parse(state_value), pendulum.parse(record_value))
        if potentially_new_records_in_the_past:
            max_cursor = record_value

        return {
            self.cursor_field: str(max_cursor),
            "include_deleted": self._include_deleted,
        }

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """Include state filter"""
        params = super().request_params(**kwargs)
        params = deep_merge(params, self._state_filter(stream_state=stream_state or {}))
        return params

    def _state_filter(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Additional filters associated with state if any set"""
        state_value = stream_state.get(self.cursor_field)
        filter_value = self._start_date if not state_value else pendulum.parse(state_value)

        potentially_new_records_in_the_past = self._include_deleted and not stream_state.get("include_deleted", False)
        if potentially_new_records_in_the_past:
            self.logger.info(f"Ignoring bookmark for {self.name} because of enabled `include_deleted` option")
            filter_value = self._start_date

        return {
            "filtering": [
                {
                    "field": f"{self.entity_prefix}.{self.cursor_field}",
                    "operator": "GREATER_THAN",
                    "value": filter_value.int_timestamp,
                },
            ],
        }


class FBMarketingReversedIncrementalStream(FBMarketingIncrementalStream, ABC):
    """The base class for streams that don't support filtering and return records sorted desc by cursor_value"""

    enable_deleted = False  # API don't have any filtering, so implement include_deleted in code

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cursor_value = None
        self._max_cursor_value = None

    @property
    def state(self) -> Mapping[str, Any]:
        """State getter, get current state and serialize it to emmit Airbyte STATE message"""
        if self._cursor_value:
            return {
                self.cursor_field: self._cursor_value,
                "include_deleted": self._include_deleted,
            }

        return {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        """State setter, ignore state if current settings mismatch saved state"""
        if self._include_deleted and not value.get("include_deleted"):
            logger.info(f"Ignoring bookmark for {self.name} because of enabled `include_deleted` option")
            return

        self._cursor_value = pendulum.parse(value[self.cursor_field])

    def _state_filter(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Don't have classic cursor filtering"""
        return {}

    def get_record_deleted_status(self, record) -> bool:
        return False

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Main read method used by CDK
        - save initial state
        - save maximum value (it is the first one)
        - update state only when we reach the end
        - stop reading when we reached the end
        """
        records_iter = self.list_objects(params=self.request_params(stream_state=stream_state))
        for record in records_iter:
            record_cursor_value = pendulum.parse(record[self.cursor_field])
            if self._cursor_value and record_cursor_value < self._cursor_value:
                break
            if not self._include_deleted and self.get_record_deleted_status(record):
                continue

            self._max_cursor_value = self._max_cursor_value or record_cursor_value
            self._max_cursor_value = max(self._max_cursor_value, record_cursor_value)
            yield record.export_all_data()

        self._cursor_value = self._max_cursor_value
