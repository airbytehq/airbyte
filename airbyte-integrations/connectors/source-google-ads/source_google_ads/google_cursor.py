# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition


class GoogleAdsCursor(ConcurrentCursor):
    def close_partition(self, partition: Partition) -> None:
        customer_id = partition.to_slice()["customer_id"]
        slice_count_before = len(self.state.get(customer_id, {}).get("slices", []))
        self._add_slice_to_state(partition)
        if slice_count_before < len(self.state.get(customer_id, {})["slices"]):  # only emit if at least one slice has been processed
            self.state[customer_id]["slices"] = self._connector_state_converter.merge_intervals(self.state[customer_id]["slices"])
            self._emit_state_message()

    def _add_slice_to_state(self, partition: Partition) -> None:
        customer_id = partition.to_slice()["customer_id"]
        if "slices" not in self.state.get(customer_id, {}):
            raise RuntimeError(
                f"The state for stream {self._stream_name} should have at least one slice to delineate the sync start time, but no "
                f"slices are present. This is unexpected. Please contact Support."
            )
        self.state[customer_id]["slices"].append(
            {
                "start": self._extract_from_slice(partition, self._slice_boundary_fields[self._START_BOUNDARY]),
                "end": self._extract_from_slice(partition, self._slice_boundary_fields[self._END_BOUNDARY]),
            }
        )
