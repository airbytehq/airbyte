#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream


def read_full_refresh(stream_instance: Stream):
    records = []
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        records.extend(list(stream_instance.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh)))
    return records


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]):
    records = []
    stream_instance.state = stream_state
    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    for slice in slices:
        records.extend(list(stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=slice, stream_state=stream_state)))
    stream_state.clear()
    stream_state.update(stream_instance.state)
    return records


class FakeInsightAsyncJobManager:
    def __init__(self, jobs, **kwargs):
        self.jobs = jobs

    def completed_jobs(self):
        yield from self.jobs


class FakeInsightAsyncJob:
    updated_insights = {}

    @classmethod
    def update_insight(cls, date_start, updated_time):
        cls.updated_insights[date_start] = updated_time

    def __init__(self, interval, **kwargs):
        self.interval = interval

    def get_result(self):
        return [self]

    def export_all_data(self):
        date_start = str(self.interval.start)
        return {"date_start": date_start, "updated_time": self.updated_insights.get(date_start, date_start)}
