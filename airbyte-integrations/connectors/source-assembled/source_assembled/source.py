#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator
from pendulum import DateTime, Period

PAGE_LIMIT = 500
BASE_URL = "https://api.assembledhq.com/v0/"

logger = logging.getLogger("airbyte")


class AssembledStream(HttpStream, ABC):
    primary_key = "id"
    data_field = "data"
    result_is_dict = True

    url_base = BASE_URL

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        total = data.get("total", 0)
        offset = data.get("offset", 0)
        return offset + PAGE_LIMIT if offset + PAGE_LIMIT < total else None

    def request_params(
        self, stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        stream_slice = stream_slice or {}
        return {
            "limit": PAGE_LIMIT,
            "offset": next_page_token or 0,
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        result = response.json()
        data = result.get(self.data_field, {})
        data = data.values() if self.result_is_dict else data

        for record in data:
            yield record

        # Rate limit 5 requests per second
        time.sleep(0.2)


class ActivityTypes(AssembledStream):
    data_field = "activity_types"

    def path(self, **kwargs) -> str:
        return "activity_types"


class FiltersSites(AssembledStream):
    data_field = "sites"

    def path(self, **kwargs) -> str:
        return "sites"


class FiltersSkills(AssembledStream):
    data_field = "skills"

    def path(self, **kwargs) -> str:
        return "skills"


class FiltersTeams(AssembledStream):
    data_field = "teams"

    def path(self, **kwargs) -> str:
        return "teams"


class FiltersQueues(AssembledStream):
    data_field = "queues"

    def path(self, **kwargs) -> str:
        return "queues"


class People(AssembledStream):
    data_field = "people"

    def path(self, **kwargs) -> str:
        return "people"


class RequirementTypes(AssembledStream):
    data_field = "requirement_types"

    def path(self, **kwargs) -> str:
        return "requirement_types"


def chunk_date_range(start_date: DateTime, interval=pendulum.duration(days=1), end_date: Optional[DateTime] = None) -> Iterable[Period]:
    """
    Yields a list of the beginning and ending timestamps of each day between the start date and now.
    The return value is a pendulum.period
    """
    end_date = end_date or pendulum.now("UTC").start_of("day")

    chunk_start_date = start_date.start_of("day")
    while chunk_start_date < end_date:
        chunk_end_date = min(chunk_start_date + interval, end_date)
        yield pendulum.period(chunk_start_date, chunk_end_date)
        chunk_start_date = chunk_end_date


###
# Important considerations for incremental streams
# Assembled allows you to retrieve events within an interval (fe.: 2022-01-01T00:00:00Z - 2022-01-01T23:59:59Z)
# New "events" can be created or old ones updated within that interval, retroactively
# If you always want to most up to date set of records for an interval, you need to sync this stream as a full refresh
###
class IncrementalAssembledStream(AssembledStream, ABC):
    paginate = False
    fetch_future_data = False

    cursor_field = "start_time"
    _cursor_value = None

    def __init__(self, default_start_date: DateTime, history_days: int, future_days: int, channels: List[str] = None, **kwargs):
        self._channels = channels or []
        self._history_days = history_days
        self._future_days = future_days
        self._start_ts = default_start_date
        super().__init__(**kwargs)

    @property
    def state(self) -> str:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = max(value[self.cursor_field], self._cursor_value or self._start_ts.int_timestamp)

    def request_params(
        self,
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
        **kwargs,
    ) -> MutableMapping[str, Any]:
        stream_slice = stream_slice or {}
        pagination_params = (
            {
                "limit": PAGE_LIMIT,
                "offset": next_page_token or 0,
            }
            if self.paginate
            else {}
        )
        return {
            **pagination_params,
            **stream_slice,
        }

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        # Incremental logic
        # 1. If no stream state sync all data from default start date
        # 2. If stream state and date diff > 1 -> sync `config.history_days` days of data from today (get updates of existing objects)
        # 3. If stream state and date diff < 1 -> sync 1 day of data from today (get updates of today's objects, avoids syncing 30 days of data every time on the same day)
        state_ts = pendulum.from_timestamp(stream_state.get(self.cursor_field)) if stream_state else None

        current_time = pendulum.now("UTC")
        current_date = current_time.start_of("day")

        end_ts = current_date
        if self.fetch_future_data:
            end_ts += pendulum.duration(days=self._future_days)
            logger.info(f"Syncing {self._future_days} days of future data for stream {self.name}")

        start_ts = self._start_ts
        if state_ts and sync_mode == SyncMode.incremental:
            days_diff = current_date.diff(state_ts).in_days()
            days = self._history_days if days_diff >= 1 else 1
            logger.info(f"Syncing {days} for stream {self.name}")
            start_ts = current_date - pendulum.duration(days=days)

        for period in chunk_date_range(start_date=start_ts, end_date=end_ts):
            period_unix = {"start_time": period.start.int_timestamp, "end_time": period.end.int_timestamp}
            if self._channels:
                for channel in self._channels:
                    yield {**period_unix, "channel": channel}
            else:
                yield period_unix

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        kwargs["stream_slice"] = stream_slice
        extract_dt = pendulum.now("UTC").int_timestamp

        # adding an extract dt helps incremental append or full sync append
        # delineate between old and new versions of the same record
        for record in super().parse_response(response, **kwargs):
            yield {
                **record,
                "_ab_extracted_at": extract_dt,
            }

        # Note 1
        # We use the end_time from the stream_slice here to set as the new cursor value. We're syncing
        # within an interval and use that intervals end_time as a starting point for the next.
        # BUT we're using start_time as cursor field for this stream so that incremental acceptance tests pass
        # and record[cursor_field] <= state_value
        # Note 2
        # When retrieving events within an given interval (fe.: 2022-01-01T00:00, 2022-01-02T18:00)
        # events that have a start_time within that interval are returned, they can have an end time > interval end_time
        new_cursor = stream_slice.get("end_time")
        self._cursor_value = max(self._cursor_value or self._start_ts.int_timestamp, new_cursor)


class ReportRequestStream(IncrementalAssembledStream, ABC):
    http_method = "POST"

    paginate = False

    cursor_field = "_ab_last_synced_at"
    _cursor_value = None

    def __init__(
        self,
        report_name: str,
        **kwargs,
    ):
        self.report_name = report_name
        super().__init__(**kwargs)

    @property
    def use_cache(self):
        return True

    @property
    def name(self) -> str:
        return self.report_name

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        yield from super().stream_slices(**kwargs)
        self._cursor_value = pendulum.now("UTC").int_timestamp

    def request_body_json(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping]:
        stream_slice = stream_slice or {}
        return {
            "interval": "30m",
            **stream_slice,
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # - One request per second to avoid rate limiting
        # - Sleeping before sending the response to avoid report still being "in_progress"
        #   when it hits the sub stream
        time.sleep(1)
        yield {
            **response.json(),
            self.cursor_field: self._cursor_value,
            "_ab_extracted_at": pendulum.now("UTC"),
        }

    def path(self, **kwargs) -> str:
        return f"reports/{self.report_name}"


class ReportStream(HttpSubStream, AssembledStream):
    primary_key = None

    data_field = "metrics"
    cursor_field = "_ab_last_synced_at"
    _cursor_value = None

    report_name = None

    def __init__(self, parent: ReportRequestStream, **kwargs):
        if not self.report_name:
            raise ValueError("ReportStream must have a report_name")

        super().__init__(parent=parent, **kwargs)

    @property
    def state(self) -> str:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def should_retry(self, response: requests.Response) -> bool:
        result = response.json()
        return super().should_retry(response) or result.get("status", "failed") != "complete"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        total = data.get("total_metric_count", 0)

        parsed_url = urlparse(response.request.url)
        offset = int(parse_qs(parsed_url.query).get("offset", ["0"])[0])

        return offset + PAGE_LIMIT if offset + PAGE_LIMIT < total else None

    def request_params(
        self, stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        stream_slice = stream_slice or {}
        return {
            "limit": PAGE_LIMIT,
            "offset": next_page_token or 0,
        }

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        self._cursor_value = pendulum.now("UTC").int_timestamp

        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            for record in parent_records:
                yield {"parent": {**stream_slice, **record}}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        parent_slice = stream_slice.get("parent", {})
        report_id = parent_slice.get("report_id")
        return f"reports/{report_id}"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, any] = None, **kwargs) -> Iterable[Mapping]:
        result = response.json()
        status = result.get("status", "failed")

        if status != "complete":
            # Report was generated and returned as a 200 but
            # the report status in the payload is not "complete".
            logger.warning(f"Report {self.report_name} failed with status: {status}")
            return []

        created_at = pendulum.parse(result.get("created_at"))
        parent_slice = stream_slice.get("parent", {})

        data = result.get(self.data_field, [])
        extracted_dt = pendulum.now("UTC").int_timestamp

        for record in data:
            attributes = record.pop("attributes", {})
            yield {
                **record,
                **attributes,
                "report": self.report_name,
                "report_id": parent_slice.get("report_id"),
                "channel": parent_slice.get("channel"),
                "created_at": created_at.int_timestamp,
                self.cursor_field: self._cursor_value,
                "_ab_extracted_at": extracted_dt,
            }

        # Rate limit 5 request per second
        time.sleep(0.2)


class AdherenceReport(ReportStream):
    report_name = "adherence"


class AgentTicketStatsReport(ReportStream):
    report_name = "agent_ticket_stats"


class Activities(IncrementalAssembledStream):
    data_field = "activities"
    fetch_future_data = True

    def path(self, **kwargs) -> str:
        return "activities"


class AgentStates(IncrementalAssembledStream):
    primary_key = None

    paginate = True

    data_field = "agent_states"
    result_is_dict = False

    def path(self, **kwargs) -> str:
        return "agents/state"


class EventChanges(IncrementalAssembledStream):
    paginate = True

    cursor_field = "modified_at"
    data_field = "event_changes"

    def path(self, **kwargs) -> str:
        return "event_changes"


class Requirements(IncrementalAssembledStream):
    primary_key = "requirement_type_id"

    data_field = "requirements"
    result_is_dict = False

    def path(self, **kwargs) -> str:
        return "requirements"


class Forecasts(IncrementalAssembledStream):
    primary_key = None

    data_field = "forecasts"
    result_is_dict = False
    fetch_future_data = True

    def path(self, **kwargs) -> str:
        return "forecasts"


# Source
class SourceAssembled(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = BasicHttpAuthenticator(username=config.get("api_key"), password="")
            people_stream = People(authenticator=auth)
            next(people_stream.read_records(SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return (False, f"Got an exception while trying to set up the connection: {e}. ")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = BasicHttpAuthenticator(username=config.get("api_key"), password="")

        default_start_date = pendulum.parse(config.get("start_date"))

        future_days = config.get("future_days", 60)
        history_days = config.get("history_days", 30)
        report_channels = config.get("report_channels", ["phone", "email"])
        forecast_channels = config.get("forecast_channels", ["phone", "email"])

        kwargs = {
            "authenticator": auth,
            "default_start_date": default_start_date,
            "history_days": history_days,
            "future_days": future_days,
        }

        forecasts_kwargs = {
            **kwargs,
            "channels": forecast_channels,
        }

        report_kwargs = {
            **kwargs,
            "channels": report_channels,
        }

        adherence_report_requests = ReportRequestStream(report_name="adherence", **report_kwargs)
        agent_ticket_stats_report_requests = ReportRequestStream(report_name="agent_ticket_stats", **report_kwargs)

        return [
            ActivityTypes(authenticator=auth),
            FiltersQueues(authenticator=auth),
            FiltersSites(authenticator=auth),
            FiltersSkills(authenticator=auth),
            FiltersTeams(authenticator=auth),
            People(authenticator=auth),
            RequirementTypes(authenticator=auth),
            Activities(**kwargs),
            AgentStates(**kwargs),
            EventChanges(**kwargs),
            Forecasts(**forecasts_kwargs),
            Requirements(**kwargs),
            AdherenceReport(authenticator=auth, parent=adherence_report_requests),
            AgentTicketStatsReport(authenticator=auth, parent=agent_ticket_stats_report_requests),
        ]
