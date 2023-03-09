#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Union

import airbyte_cdk.sources.utils.casing as casing
import pendulum
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.utils import AirbyteTracedException
from cached_property import cached_property
from facebook_business.exceptions import FacebookBadObjectError
from source_facebook_marketing.streams.async_job import AsyncJob, InsightAsyncJob, ParentAsyncJob
from source_facebook_marketing.streams.async_job_manager import InsightAsyncJobManager

from .base_streams import FBMarketingIncrementalStream

logger = logging.getLogger("airbyte")


class AdsInsights(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/insights"""

    cursor_field = "date_start"
    use_batch = False
    enable_deleted = False

    ALL_ACTION_ATTRIBUTION_WINDOWS = [
        "1d_click",
        "7d_click",
        "28d_click",
        "1d_view",
        "7d_view",
        "28d_view",
    ]

    ALL_ACTION_BREAKDOWNS = [
        "action_type",
        "action_target_id",
        "action_destination",
    ]

    # Facebook store metrics maximum of 37 months old. Any time range that
    # older that 37 months from current date would result in 400 Bad request
    # HTTP response.
    # https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
    INSIGHTS_RETENTION_PERIOD = pendulum.duration(months=37)

    action_breakdowns = ALL_ACTION_BREAKDOWNS
    level = "ad"
    action_attribution_windows = ALL_ACTION_ATTRIBUTION_WINDOWS
    time_increment = 1

    breakdowns = []

    def __init__(
        self,
        name: str = None,
        fields: List[str] = None,
        breakdowns: List[str] = None,
        action_breakdowns: List[str] = None,
        time_increment: Optional[int] = None,
        insights_lookback_window: int = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._start_date = self._start_date.date()
        self._end_date = self._end_date.date()
        self._fields = fields
        self.action_breakdowns = action_breakdowns or self.action_breakdowns
        self.breakdowns = breakdowns or self.breakdowns
        self.time_increment = time_increment or self.time_increment
        self._new_class_name = name
        self._insights_lookback_window = insights_lookback_window

        # state
        self._cursor_value = {}  # latest period that was read
        self._next_cursor_value = self._get_start_date()
        self._completed_slices = {}

    @property
    def name(self) -> str:
        """We override stream name to let the user change it via configuration."""
        name = self._new_class_name or self.__class__.__name__
        return casing.camel_to_snake(name)

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """Build complex PK based on slices and breakdowns"""
        return ["date_start", "account_id", "ad_id"] + self.breakdowns

    @property
    def insights_lookback_period(self):
        """
        Facebook freezes insight data 28 days after it was generated, which means that all data
        from the past 28 days may have changed since we last emitted it, so we retrieve it again.
        But in some cases users my have define their own lookback window, thats
        why the value for `insights_lookback_window` is set throught config.
        """
        return pendulum.duration(days=self._insights_lookback_window)

    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        """Because insights has very different read_records we don't need this method anymore"""

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Waits for current job to finish (slice) and yield its result"""
        job = stream_slice["insight_job"]

        try:
            for obj in job.get_result():
                yield obj.export_all_data()
        except FacebookBadObjectError as e:
            raise AirbyteTracedException(
                message=f"API error occurs on Facebook side during job: {job}, wrong (empty) response received with errors: {e} "
                        f"Please try again later",
                failure_type=FailureType.system_error,
            ) from e


        # job = InsightAsyncJob(api=job._api, interval=job.interval, edge_object=job.edge_object, params=job._params)
        # job = ParentAsyncJob(jobs=[job], api=job._api, interval=job.interval)
        if type(job) != ParentAsyncJob:
            account_id = job.edge_object.get("account_id")
        else:
            # TODO: At this point we would sometimes get ParentAsyncJob. Should not happen. To debug.
            # In the meantime we get the account ID of the 1st job
            self.logger.error("This job {} has no edge_object. It is of type {}".format(str(job), str(type(job))))
            if type(job) == ParentAsyncJob:
                self.logger.error("This group of jobs has the following jobs : ")
                for j in job._jobs:
                    self.logger.error(str(j))
            self.logger.error("We will select the account ID of the first job of the list of jobs")
            account_id = job._jobs[0].edge_object.get("account_id")

        self._completed_slices[account_id] = self._completed_slices.get(account_id, set())
        self._completed_slices[account_id].add(job.interval.start)
        if job.interval.start == self._next_cursor_value.get(account_id, self._next_cursor_value.get(None)):
            self._advance_cursor(account_id)

    @property
    def state(self) -> MutableMapping[str, Any]:
        """State getter, the result can be stored by the source"""
        if len(self._cursor_value):
            return {
                k: {
                    self.cursor_field: v.isoformat(),
                    "slices": [d.isoformat() for d in list(self._completed_slices.get(k, set()))],
                    "time_increment": self.time_increment,
                }
                for k,v in {**self._next_cursor_value, **self._cursor_value}.items() if k
            }

        if len(self._completed_slices):
            return {
                k: {
                    "slices": [d.isoformat() for d in v],
                    "time_increment": self.time_increment,
                }
                for k,v in self._completed_slices.items()
            }

        return {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        """State setter, will ignore saved state if time_increment is different from previous."""
        # if the time increment configured for this stream is different from the one in the previous state
        # then the previous state object is invalid and we should start replicating data from scratch
        # to achieve this, we skip setting the state

        for k,v in value.items():
            if v.get("time_increment", 1) != self.time_increment:
                logger.info(f"Ignoring bookmark for {self.name} account[{k}] because of different `time_increment` option.")
                continue

            self._cursor_value = {**self._cursor_value, k: pendulum.parse(v[self.cursor_field]).date() if v.get(self.cursor_field) else None}
            self._completed_slices = {**self._completed_slices, k: set(pendulum.parse(_v).date() for _v in v.get("slices", []))}
            self._next_cursor_value = {**self._next_cursor_value, **self._get_start_date(k)}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """Update stream state from latest record

        :param current_stream_state: latest state returned
        :param latest_record: latest record that we read
        """
        return self.state

    def _date_intervals(self, account_id:str=None) -> Iterator[pendulum.Date]:
        """Get date period to sync"""
        next_cursor_value = self._next_cursor_value.get(account_id, self._next_cursor_value.get(None))
        if self._end_date < next_cursor_value:
            return
        date_range = self._end_date - next_cursor_value
        yield from date_range.range("days", self.time_increment)

    def _advance_cursor(self, account_id:str=None):
        """Iterate over state, find continuing sequence of slices. Get last value, advance cursor there and remove slices from state"""
        for ts_start in self._date_intervals(account_id=account_id):
            if ts_start not in self._completed_slices.get(account_id, set()):
                self._next_cursor_value[account_id] = ts_start
                break
            self._completed_slices[account_id].remove(ts_start)
            self._cursor_value[account_id] = ts_start

    def _generate_async_jobs(self, params: Mapping) -> Iterator[AsyncJob]:
        """Generator of async jobs

        :param params:
        :return:
        """
        for account in self._api.accounts:
            for ts_start in self._date_intervals(account_id=account.get("account_id")):
                if ts_start in self._completed_slices.get(account.get("account_id"), set()):
                    continue
                ts_end = ts_start + pendulum.duration(days=self.time_increment - 1)
                interval = pendulum.Period(ts_start, ts_end)
                yield InsightAsyncJob(api=self._api.api, edge_object=account, interval=interval, params=params)

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:

        """Slice by date periods and schedule async job for each period, run at most MAX_ASYNC_JOBS jobs at the same time.
        This solution for Async was chosen because:
        1. we should commit state after each successful job
        2. we should run as many job as possible before checking for result
        3. we shouldn't proceed to consumption of the next job before previous succeed

        generate slice only if it is not in state,
        when we finished reading slice (in read_records) we check if current slice is the next one and do advance cursor

        when slice is not next one we just update state with it
        to do so source will check state attribute and call get_state,
        """
        if stream_state:
            self.state = stream_state

        manager = InsightAsyncJobManager(api=self._api, jobs=self._generate_async_jobs(params=self.request_params()))
        for job in manager.completed_jobs():
            yield {"insight_job": job}

    def _get_start_date(self, account_id:str=None) -> pendulum.Date:
        """Get start date to begin sync with. It is not that trivial as it might seem.
        There are few rules:
            - don't read data older than start_date
            - re-read data within last 28 days
            - don't read data older than retention date
        Also there are difference between start_date and cursor_value in how the value must be interpreted:
            - cursor - last value that we synced
            - start_date - the first value that should be synced

        :return: the first date to sync
        """
        today = pendulum.today().date()
        oldest_date = today - self.INSIGHTS_RETENTION_PERIOD
        refresh_date = today - self.insights_lookback_period
        if (self._cursor_value or {}).get(account_id):
            start_date = self._cursor_value.get(account_id) + pendulum.duration(days=self.time_increment)
            if start_date > refresh_date:
                logger.info(
                    f"The cursor value within refresh period ({self.insights_lookback_period}), start sync from {refresh_date} instead."
                )
            start_date = min(start_date, refresh_date)

            if start_date < self._start_date:
                logger.warning(f"Ignore provided state and start sync from start_date ({self._start_date}).")
            start_date = max(start_date, self._start_date)
        else:
            start_date = self._start_date
        if start_date < oldest_date:
            logger.warning(f"Loading insights older then {self.INSIGHTS_RETENTION_PERIOD} is not possible. Start sync from {oldest_date}.")

        return {account_id: max(oldest_date, start_date)}

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {
            "level": self.level,
            "action_breakdowns": self.action_breakdowns,
            "breakdowns": self.breakdowns,
            "fields": self.fields,
            "time_increment": self.time_increment,
            "action_attribution_windows": self.action_attribution_windows,
        }

    def _state_filter(self, stream_slice: dict, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Works differently for insights, so remove it"""
        return {}

    def get_json_schema(self) -> Mapping[str, Any]:
        """Add fields from breakdowns to the stream schema
        :return: A dict of the JSON schema representing this stream.
        """
        loader = ResourceSchemaLoader(package_name_from_class(self.__class__))
        schema = loader.get_schema("ads_insights")
        if self._fields:
            schema["properties"] = {k: v for k, v in schema["properties"].items() if k in self._fields + [self.cursor_field]}
        if self.breakdowns:
            breakdowns_properties = loader.get_schema("ads_insights_breakdowns")["properties"]
            schema["properties"].update({prop: breakdowns_properties[prop] for prop in self.breakdowns})
        return schema

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        if self._fields:
            return self._fields
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("ads_insights")
        return list(schema.get("properties", {}).keys())
