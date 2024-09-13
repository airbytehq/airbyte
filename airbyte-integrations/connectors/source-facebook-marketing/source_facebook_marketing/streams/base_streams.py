#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cache
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
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

    valid_statuses = []
    status_field = ""
    # entity prefix for statuses filter, it usually matches singular version of stream name
    entity_prefix = None
    # In case of Error 'Too much data was requested in batch' some fields should be removed from request
    fields_exceptions = []

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def __init__(
        self,
        api: "API",
        account_ids: List[str],
        filter_statuses: list = [],
        page_size: int = 100,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._api = api
        self._account_ids = account_ids
        self.page_size = page_size if page_size is not None else 100
        self._filter_statuses = filter_statuses
        self._fields = None
        self._saved_fields = None

    @cache
    def fields(self, **kwargs) -> List[str]:
        """
        List of fields that we want to query, if no json_schema from configured catalog then will get all properties from stream's schema
        """
        if self._fields:
            return self._fields
        json_schema = (
            self.configured_json_schema
            if self.configured_json_schema and self.configured_json_schema.get("properties")
            else self.get_json_schema()
        )
        self._saved_fields = list(json_schema.get("properties", {}).keys())
        return self._saved_fields

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

    @staticmethod
    def add_account_id(record, account_id: str):
        if "account_id" not in record:
            record["account_id"] = account_id

    def get_account_state(self, account_id: str, stream_state: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        """
        Retrieve the state for a specific account.

        If multiple account IDs are present, the state for the specific account ID
        is returned if it exists in the stream state. If only one account ID is
        present, the entire stream state is returned.

        :param account_id: The account ID for which to retrieve the state.
        :param stream_state: The current stream state, optional.
        :return: The state information for the specified account as a MutableMapping.
        """
        if stream_state and account_id and account_id in stream_state:
            account_state = stream_state.get(account_id)

            # copy `include_deleted` from general stream state
            if "include_deleted" in stream_state:
                account_state["include_deleted"] = stream_state["include_deleted"]
            return account_state
        elif len(self._account_ids) == 1:
            return stream_state
        else:
            return {}

    def _transform_state_from_one_account_format(self, state: Mapping[str, Any], move_fields: List[str] = None) -> Mapping[str, Any]:
        """
        Transforms the state from an old format to a new format based on account IDs.

        This method transforms the old state to be a dictionary where the keys are account IDs.
        If the state is in the old format (not keyed by account IDs), it will transform the state
        by nesting it under the account ID.

        :param state: The original state dictionary to transform.
        :param move_fields: A list of field names whose values should be moved to the top level of the new state dictionary.
        :return: The transformed state dictionary.
        """

        # If the state already contains any of the account IDs, return the state as is.
        for account_id in self._account_ids:
            if account_id in state:
                return state

        # Handle the case where there is only one account ID.
        # Transform the state by nesting it under the account ID.
        if state and len(self._account_ids) == 1:
            account_id = self._account_ids[0]
            new_state = {account_id: state}

            # Move specified fields to the top level of the new state.
            if move_fields:
                for move_field in move_fields:
                    if move_field in state:
                        new_state[move_field] = state.pop(move_field)

            return new_state

        # If the state is empty or there are multiple account IDs, return an empty dictionary.
        return {}

    def _transform_state_from_old_deleted_format(self, state: Mapping[str, Any]):
        # transform from the old format with `include_deleted`
        for account_id in self._account_ids:
            account_state = state.get(account_id, {})
            # check if the state for this account id is in the old format
            if "filter_statuses" not in account_state and "include_deleted" in account_state:
                if account_state["include_deleted"]:
                    account_state["filter_statuses"] = self.valid_statuses
                else:
                    account_state["filter_statuses"] = []
                state[account_id] = account_state
        return state

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Main read method used by CDK"""
        account_id = stream_slice["account_id"]
        account_state = stream_slice.get("stream_state", {})

        try:
            for record in self.list_objects(
                params=self.request_params(stream_state=account_state),
                account_id=account_id,
            ):
                if isinstance(record, AbstractObject):
                    record = record.export_all_data()  # convert FB object to dict
                self.fix_date_time(record)
                self.add_account_id(record, stream_slice["account_id"])
                yield record
        except FacebookRequestError as exc:
            raise traced_exception(exc)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        if stream_state:
            stream_state = self._transform_state_from_one_account_format(stream_state, ["include_deleted"])
            stream_state = self._transform_state_from_old_deleted_format(stream_state)

        for account_id in self._account_ids:
            account_state = self.get_account_state(account_id, stream_state)
            yield {"account_id": account_id, "stream_state": account_state}

    @abstractmethod
    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        """List FB objects, these objects will be loaded in read_records later with their details.

        :param params: params to make request
        :return: list of FB objects to load
        """

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        """Parameters that should be passed to query_records method"""
        params = {"limit": self.page_size}
        params.update(self._filter_all_statuses())

        return params

    def _filter_all_statuses(self) -> MutableMapping[str, Any]:
        """Filter records by statuses"""

        return (
            {
                "filtering": [
                    {
                        "field": f"{self.entity_prefix}.{self.status_field}",
                        "operator": "IN",
                        "value": self._filter_statuses,
                    },
                ],
            }
            if self._filter_statuses and self.status_field
            else {}
        )


class FBMarketingIncrementalStream(FBMarketingStream, ABC):
    """Base class for incremental streams"""

    cursor_field = "updated_time"

    def __init__(self, start_date: Optional[datetime], end_date: Optional[datetime], **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.instance(start_date) if start_date else None
        self._end_date = pendulum.instance(end_date) if end_date else None

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ):
        """Update stream state from latest record"""
        account_id = latest_record["account_id"]
        state_for_accounts = self._transform_state_from_one_account_format(current_stream_state, ["include_deleted"])
        state_for_accounts = self._transform_state_from_old_deleted_format(state_for_accounts)
        account_state = self.get_account_state(account_id, state_for_accounts)

        potentially_new_records_in_the_past = self._filter_statuses and (
            set(self._filter_statuses) - set(account_state.get("filter_statuses", []))
        )
        record_value = latest_record[self.cursor_field]
        state_value = account_state.get(self.cursor_field) or record_value
        max_cursor = max(pendulum.parse(state_value), pendulum.parse(record_value))
        if potentially_new_records_in_the_past:
            max_cursor = record_value

        state_for_accounts.setdefault(account_id, {})[self.cursor_field] = str(max_cursor)
        state_for_accounts[account_id]["filter_statuses"] = self._filter_statuses

        return state_for_accounts

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """Include state filter"""
        params = super().request_params(**kwargs)
        params = deep_merge(params, self._state_filter(stream_state=stream_state or {}))
        return params

    def _state_filter(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Additional filters associated with state if any set"""

        state_value = stream_state.get(self.cursor_field)
        if stream_state and state_value:
            filter_value = pendulum.parse(state_value)
        elif self._start_date:
            filter_value = self._start_date
        else:
            # if start_date is not specified then do not use date filters
            return {}

        potentially_new_records_in_the_past = set(self._filter_statuses) - set(stream_state.get("filter_statuses", []))

        if potentially_new_records_in_the_past:
            self.logger.info(f"Ignoring bookmark for {self.name} because `filter_statuses` were changed.")
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cursor_values = {}

    @property
    def state(self) -> Mapping[str, Any]:
        """State getter, get current state and serialize it to emmit Airbyte STATE message"""
        if self._cursor_values:
            result_state = {account_id: {self.cursor_field: cursor_value} for account_id, cursor_value in self._cursor_values.items()}
            result_state["filter_statuses"] = self._filter_statuses
            return result_state

        return {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        """State setter, ignore state if current settings mismatch saved state"""
        transformed_state = self._transform_state_from_one_account_format(value, ["include_deleted"])
        transformed_state = self._transform_state_from_old_deleted_format(transformed_state)

        if set(self._filter_statuses) - set(transformed_state.get("filter_statuses", [])):
            logger.info(f"Ignoring bookmark for {self.name} because of enabled `filter_statuses` option")
            return

        self._cursor_values = {}
        for account_id in self._account_ids:
            cursor_value = transformed_state.get(account_id, {}).get(self.cursor_field)
            if cursor_value is not None:
                self._cursor_values[account_id] = cursor_value

    def _state_filter(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Don't have classic cursor filtering"""
        return {}

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
        account_id = stream_slice["account_id"]
        account_state = stream_slice.get("stream_state")

        try:
            records_iter = self.list_objects(
                params=self.request_params(stream_state=account_state),
                account_id=account_id,
            )
            account_cursor = self._cursor_values.get(account_id)

            max_cursor_value = None
            for record in records_iter:
                record_cursor_value = record[self.cursor_field]
                if account_cursor and record_cursor_value < account_cursor:
                    break

                max_cursor_value = max(max_cursor_value, record_cursor_value) if max_cursor_value else record_cursor_value
                record = record.export_all_data()
                self.fix_date_time(record)
                self.add_account_id(record, stream_slice["account_id"])
                yield record

            self._cursor_values[account_id] = max_cursor_value
        except FacebookRequestError as exc:
            raise traced_exception(exc)
