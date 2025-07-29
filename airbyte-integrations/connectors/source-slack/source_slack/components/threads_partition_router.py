# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import timedelta

from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.types import StreamState
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse


class ThreadsPartitionRouter(SubstreamPartitionRouter):
    """
    The logic for incrementally syncing threads is not very obvious, so buckle up.
    To get all messages in a thread, one must specify the channel and timestamp of the parent (first) message of that thread,
    basically its ID.
    One complication is that threads can be updated at Any time in the future. Therefore, if we wanted to comprehensively sync data
    i.e: get every single response in a thread, we'd have to read every message in the slack instance every time we ran a sync,
    because otherwise there is no way to guarantee that a thread deep in the past didn't receive a new message.
    A pragmatic workaround is to say we want threads to be at least N days fresh i.e: look back N days into the past,
    get every message since, and read all of the thread responses. This is essentially the approach we're taking here via slicing:
    create slices from N days into the past and read all messages in threads since then. We could optionally filter out records we have
    already read, but that's omitted to keep the logic simple to reason about.
    Good luck.
    """

    def set_initial_state(self, stream_state: StreamState) -> None:
        if not stream_state:
            return

        start_date_state = ab_datetime_parse(self.config["start_date"]).timestamp()  # start date is required
        # for migrated state
        if stream_state.get("states"):
            for state in stream_state["states"]:
                start_date_state = max(start_date_state, float(state.get("cursor", {}).get("float_ts", start_date_state)))
        # for old-stype state
        if stream_state.get("float_ts"):
            start_date_state = max(start_date_state, float(stream_state["float_ts"]))

        lookback_window = timedelta(days=self.config.get("lookback_window", 0))  # lookback window in days
        final_state = {"float_ts": (ab_datetime_parse(int(start_date_state)) - lookback_window).timestamp()}
        # Set state for each parent stream with an incremental dependency
        for parent_config in self.parent_stream_configs:
            # Migrate child state to parent state format
            start_date_state = self._migrate_child_state_to_parent_state(final_state)
            parent_config.stream.state = start_date_state.get(parent_config.stream.name, {})
