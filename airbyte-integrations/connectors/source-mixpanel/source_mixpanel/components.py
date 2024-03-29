from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter

from dataclasses import InitVar, dataclass
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, Optional, Union
import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters import HttpRequester
# from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.declarative.transformations import RecordTransformation, AddFields
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Union

import dpath.util
import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config

@dataclass
class MixpanelXXXHttpRequester(HttpRequester):
    ...
    # def get_url_base(self) -> str:
    #     """
    #     REGION: url
    #     US    : https://mixpanel.com/api/2.0/
    #     EU    : https://EU.mixpanel.com/api/2.0/
    #     """
    #     url_base = super().get_url_base().replace("US.", "")
    #     return url_base

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


@dataclass
class EngageTransformation(RecordTransformation):
    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        """
        - flatten $properties fields
        - remove leading '$'
        """
        record["distinct_id"] = record.pop("$distinct_id")
        properties = record.pop("$properties")
        for property_name in properties:
            this_property_name = property_name
            if property_name.startswith("$"):
                # Just remove leading '$' for 'reserved' mixpanel properties name, example:
                # from API: '$browser'
                # to stream: 'browser'
                this_property_name = this_property_name[1:]
            record[this_property_name] = properties[property_name]

        return record


class RevenueDpathExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        """
        response.json() example:
        {
            'computed_at': '2021-07-03T12:43:48.889421+00:00',
            'results': {
                '$overall': {       <-- should be skipped
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                '2021-06-01': {
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                '2021-06-02': {
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                ...
            },
            'session_id': '162...',
            'status': 'ok'
        }
        """
        new_records = []
        for record in super().extract_records(response):
            for date_entry in record:
                if date_entry != "$overall":
                    list.append(new_records, {"date": date_entry, **record[date_entry]})
        return new_records
