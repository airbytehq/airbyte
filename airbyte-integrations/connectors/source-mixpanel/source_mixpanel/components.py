from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter

from dataclasses import InitVar, dataclass
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, Optional, Union
import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState

class CohortMembersSubstreamPartitionRouter(SubstreamPartitionRouter):

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # https://developer.mixpanel.com/reference/engage-query
        cohort_id = stream_slice["id"]
        return {"filter_by_cohort": f"{{\"id\":{cohort_id}}}"}
