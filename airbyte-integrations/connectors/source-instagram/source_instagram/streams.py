#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import json
from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from cached_property import cached_property
from source_instagram.api import InstagramAPI

from .common import remove_params_from_url


class DatetimeTransformerMixin:
    transformer: TypeTransformer = TypeTransformer(TransformConfig.CustomSchemaNormalization)

    @staticmethod
    @transformer.registerCustomTransform
    def custom_transform_datetime_rfc3339(original_value, field_schema):
        """
        Transform datetime string to RFC 3339 format
        """
        if original_value and field_schema.get("format") == "date-time" and field_schema.get("airbyte_type") == "timestamp_with_timezone":
            # Parse the ISO format timestamp
            dt = pendulum.parse(original_value)

            # Convert to RFC 3339 format
            return dt.to_rfc3339_string()
        return original_value


class InstagramStream(Stream, ABC):
    """Base stream class"""

    page_size = 100
    primary_key = "id"

    def __init__(self, api: InstagramAPI, **kwargs):
        super().__init__(**kwargs)
        self._api = api

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        non_object_fields = ["page_id", "business_account_id"]
        fields = list(self.get_json_schema().get("properties", {}).keys())
        return list(set(fields) - set(non_object_fields))

    def request_params(
        self,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """Parameters that should be passed to query_records method"""
        return {"limit": self.page_size}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override to define the slices for this stream. See the stream slicing section of the docs for more information.

        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return:
        """
        for account in self._api.accounts:
            yield {"account": account}

    def transform(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        return self._clear_url(record)

    @staticmethod
    def _clear_url(record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        This function removes the _nc_rid parameter from the video url and ccb from profile_picture_url for users.
        _nc_rid is generated every time a new one and ccb can change its value, and tests fail when checking for identity.
        This does not spoil the link, it remains correct and by clicking on it you can view the video or see picture.
        """
        if record.get("media_url"):
            record["media_url"] = remove_params_from_url(record["media_url"], params=["_nc_rid"])
        if record.get("profile_picture_url"):
            record["profile_picture_url"] = remove_params_from_url(record["profile_picture_url"], params=["ccb"])

        return record


class InstagramIncrementalStream(InstagramStream, IncrementalMixin):
    """Base class for incremental streams"""

    def __init__(self, start_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.parse(start_date)
        self._state = {}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state.update(**value)

    def _update_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """Update stream state from latest record"""
        # if there is no `end_date` value take the `start_date`
        record_value = latest_record.get(self.cursor_field) or self._start_date.to_iso8601_string()
        account_id = latest_record.get("business_account_id")
        state_value = current_stream_state.get(account_id, {}).get(self.cursor_field) or record_value
        max_cursor = max(pendulum.parse(state_value), pendulum.parse(record_value))
        new_stream_state = copy.deepcopy(current_stream_state)
        new_stream_state[account_id] = {self.cursor_field: str(max_cursor)}
        return new_stream_state


class UserInsights(DatetimeTransformerMixin, InstagramIncrementalStream):
    """Docs: https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights"""

    METRICS_BY_PERIOD = {
        "day": [
            "email_contacts",
            "follower_count",
            "get_directions_clicks",
            "impressions",
            "phone_call_clicks",
            "profile_views",
            "reach",
            "text_message_clicks",
            "website_clicks",
        ],
        "week": ["impressions", "reach"],
        "days_28": ["impressions", "reach"],
        "lifetime": ["online_followers"],
    }

    primary_key = ["business_account_id", "date"]
    cursor_field = "date"

    # For some metrics we can only get insights not older than 30 days, it is Facebook policy
    buffer_days = 30
    days_increment = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._end_date = pendulum.now()
        self.should_exit_gracefully = False

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        account = stream_slice["account"]
        ig_account = account["instagram_business_account"]
        account_id = ig_account.get("id")

        base_params = self.request_params(stream_state=stream_state, stream_slice=stream_slice)
        insight_list = []
        # iterate over each period, query insights
        for period, metrics in self.METRICS_BY_PERIOD.items():
            params = {
                **base_params,
                "metric": metrics,
                "period": [period],
            }

            # we get only first record, because cursor will try to fetch next date interval
            cursor = ig_account.get_insights(params=params)
            if len(cursor):
                insight_list += [insights.export_all_data() for insights in cursor[: len(cursor)]]

        # end then merge all periods in one record
        insight_record = {"page_id": account["page_id"], "business_account_id": account_id}
        for insight in insight_list:
            key = insight["name"]
            if insight["period"] in ["week", "days_28"]:
                key += f"_{insight['period']}"

            insight_record[key] = insight.get("values")[0]["value"]  # this depends on days_increment value
            if not insight_record.get(self.cursor_field):
                insight_record[self.cursor_field] = insight.get("values")[0]["end_time"]

        complete_records = [insight_record]
        # if insight_list is empty, we don't want to yield an incomplete record and want to stop syncing this stream gracefully
        if not insight_list:
            complete_records = []
            # https://developers.facebook.com/docs/instagram-api/guides/insights/
            # If insights data you are requesting does not exist or is currently unavailable
            # the API will return an empty data set instead of 0 for individual metrics.
            self.logger.warning(
                f"No data received for base params {json.dumps(base_params)}. "
                f"Since we can't know whether there is no data or the data is temporarily unavailable, stop syncing so as not to miss "
                f"temporarily unavailable data."
            )
            self.should_exit_gracefully = True

        yield from complete_records

        # update state using IncrementalMixin
        # reference issue: https://github.com/airbytehq/airbyte/issues/24697
        if sync_mode == SyncMode.incremental and complete_records:
            for record in complete_records:
                self.state = self._update_state(self.state, record)

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """Extend default slicing based on accounts with slices based on date intervals"""
        stream_state = stream_state or {}
        stream_slices = super().stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        for stream_slice in stream_slices:
            account = stream_slice["account"]
            account_id = account["instagram_business_account"]["id"]

            state_value = stream_state.get(account_id, {}).get(self.cursor_field)
            start_date = pendulum.parse(state_value) if state_value else self._start_date
            start_date = max(start_date, self._start_date, pendulum.now().subtract(days=self.buffer_days))
            if start_date > pendulum.now():
                continue
            for since in pendulum.period(start_date, self._end_date).range("days", self.days_increment):
                until = since.add(days=self.days_increment)
                if self.should_exit_gracefully:
                    self.logger.info(f"Stopping syncing stream '{self.name}'")
                    return
                self.logger.info(f"Reading insights between {since.date()} and {until.date()}")
                yield {
                    **stream_slice,
                    "since": since.to_datetime_string(),
                    "until": until.to_datetime_string(),  # excluding
                }

    def request_params(
        self,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """Append datetime range params"""
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice)
        return {
            **params,
            "since": stream_slice["since"],
            "until": stream_slice["until"],
        }

    def _state_has_legacy_format(self, state: Mapping[str, Any]) -> bool:
        """Tell if the format of state is outdated"""
        for value in state.values():
            if not isinstance(value, Mapping):
                return True
        return False
