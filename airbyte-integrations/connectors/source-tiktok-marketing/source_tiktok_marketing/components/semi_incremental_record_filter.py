from typing import List, Mapping, Any, Optional

from airbyte_cdk.sources.declarative.extractors import RecordFilter
from airbyte_cdk.sources.declarative.types import StreamState, StreamSlice


class PerPartitionRecordFilter(RecordFilter):
    def filter_records(
        self,
        records: List[Mapping[str, Any]],
        stream_state: StreamState,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> List[Mapping[str, Any]]:
        stream_states = [p["cursor"] for p in stream_state["states"] if p["partition"]["advertiser_id"] == stream_slice["advertiser_id"]]
        if not stream_states:
            stream_state = {}
        else:
            stream_state = stream_states[0]
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        return [record for record in records if self._filter_interpolator.eval(self.config, record=record, **kwargs)]
