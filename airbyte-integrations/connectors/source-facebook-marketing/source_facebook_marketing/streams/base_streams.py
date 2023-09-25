#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from cached_property import cached_property
from facebook_business.adobjects.abstractobject import AbstractObject
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.streams.common import traced_exception

from .common import deep_merge

if TYPE_CHECKING:  # pragma: no cover
    from source_facebook_marketing.api import API


logger = logging.getLogger("airbyte")


class FBMarketingStream(Stream, ABC):
    """Base stream class"""

    primary_key = "id"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    # this flag will override `include_deleted` option for streams that does not support it
    enable_deleted = True
    # entity prefix for `include_deleted` filter, it usually matches singular version of stream name
    entity_prefix = None
    # In case of Error 'Too much data was requested in batch' some fields should be removed from request
    fields_exceptions = []

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def __init__(self, api: "API", include_deleted: bool = False, page_size: int = 100, **kwargs):
        super().__init__(**kwargs)
        self._api = api
        self.page_size = page_size if page_size is not None else 100
        self._include_deleted = include_deleted if self.enable_deleted else False

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        return list(self.get_json_schema().get("properties", {}).keys())

    @classmethod
    def fix_date_time(cls, record):
        date_time_fields = (
            "created_time",
            "creation_time",
            "updated_time",
            "event_time",
            "start_time",
            "first_fired_time",
            "last_fired_time",
        )

        if isinstance(record, dict):
            for field, value in record.items():
                if isinstance(value, str):
                    if field in date_time_fields:
                        record[field] = value.replace("t", "T").replace(" 0000", "+0000")
                else:
                    cls.fix_date_time(value)

        elif isinstance(record, list):
            for entry in record:
                cls.fix_date_time(entry)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Main read method used by CDK"""
        try:
            for record in self.list_objects(params=self.request_params(stream_state=stream_state)):
                if isinstance(record, AbstractObject):
                    record = record.export_all_data()  # convert FB object to dict
                self.fix_date_time(record)
                yield record
        except FacebookRequestError as exc:
            raise traced_exception(exc)

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

    def __init__(self, start_date: Optional[datetime], end_date: Optional[datetime], **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.instance(start_date) if start_date else None
        self._end_date = pendulum.instance(end_date) if end_date else None

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
        if stream_state:
            filter_value = pendulum.parse(state_value)
        elif self._start_date:
            filter_value = self._start_date
        else:
            # if start_date is not specified then do not use date filters
            return {}

        potentially_new_records_in_the_past = self._include_deleted and not stream_state.get("include_deleted", False)
        if potentially_new_records_in_the_past:
            self.logger.info(f"Ignoring bookmark for {self.name} because of enabled `include_deleted` option")
            if self._start_date:
                filter_value = self._start_date
            else:
                # if start_date is not specified then do not use date filters
                return {}

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
        try:
            records_iter = self.list_objects(params=self.request_params(stream_state=stream_state))
            for record in records_iter:
                record_cursor_value = pendulum.parse(record[self.cursor_field])
                if self._cursor_value and record_cursor_value < self._cursor_value:
                    break
                if not self._include_deleted and self.get_record_deleted_status(record):
                    continue

                self._max_cursor_value = max(self._max_cursor_value, record_cursor_value) if self._max_cursor_value else record_cursor_value
                record = record.export_all_data()
                self.fix_date_time(record)
                yield record

            self._cursor_value = self._max_cursor_value
        except FacebookRequestError as exc:
            raise traced_exception(exc)
