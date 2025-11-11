from typing import Optional

from airbyte_cdk.sources.declarative.models import FailureType
from airbyte_cdk.sources.declarative.types import Record, StreamSlice
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


class PaginationTracker:
    _record_count: int
    _number_of_attempt_with_same_slice: int

    def __init__(
        self, cursor: Optional[ConcurrentCursor] = None, max_number_of_records: Optional[int] = None
    ) -> None:
        """
        Ideally, we would have passed the `Cursor` interface here instead of `ConcurrentCursor` but not all
        implementations of `Cursor` can support this use case. For example, if the `ConcurrentPerPartitionCursor`
        switch to global state, we stop keeping track of the state per partition and therefore can't get an accurate
        view for a specific stream_slice. In order to solve that, we decided to scope this feature to use only
        ConcurrentCursor which is the only "leaf" cursor that actually emits stream slices with `cursor_partition`.
        """
        self._cursor = cursor
        self._limit = max_number_of_records
        self._reset()

        """
        Given we have a cursor, we do not allow for the same slice to be processed twice because we assume we will
        always process the same slice.

        Given no cursor, we assume that the pagination reset is for retrying purposes and we allow to retry once.
        """
        self._allowed_number_of_attempt_with_same_slice = 1 if self._cursor else 2
        self._number_of_attempt_with_same_slice = 0

    def observe(self, record: Record) -> None:
        self._record_count += 1
        if self._cursor:
            self._cursor.observe(record)

    def has_reached_limit(self) -> bool:
        return self._limit is not None and self._record_count >= self._limit

    def _reset(self) -> None:
        self._record_count = 0

    def reduce_slice_range_if_possible(self, stream_slice: StreamSlice) -> StreamSlice:
        new_slice = self._cursor.reduce_slice_range(stream_slice) if self._cursor else stream_slice

        if new_slice == stream_slice:
            self._number_of_attempt_with_same_slice += 1
            if (
                self._number_of_attempt_with_same_slice
                >= self._allowed_number_of_attempt_with_same_slice
            ):
                raise AirbyteTracedException(
                    internal_message=f"There were {self._number_of_attempt_with_same_slice} attempts with the same slice already while the max allowed is {self._allowed_number_of_attempt_with_same_slice}",
                    failure_type=FailureType.system_error,
                )
        else:
            self._number_of_attempt_with_same_slice = 0

        self._reset()
        return new_slice
