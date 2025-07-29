# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse


class ThreadsPartitionRouter(SubstreamPartitionRouter):
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

        final_state = {"float_ts": start_date_state}
        # Set state for each parent stream with an incremental dependency
        for parent_config in self.parent_stream_configs:
            # Migrate child state to parent state format
            start_date_state = self._migrate_child_state_to_parent_state(final_state)
            parent_config.stream.state = start_date_state.get(parent_config.stream.name, {})
