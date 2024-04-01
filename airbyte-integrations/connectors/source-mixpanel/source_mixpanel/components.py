import base64
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator, ApiKeyAuthenticator
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter

from dataclasses import InitVar, dataclass
from typing import TYPE_CHECKING, Any, Iterable, List, Mapping, Optional, Union, Tuple, MutableMapping
import dpath.util
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator
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


# class MixpanelBearerAuthenticator(BearerAuthenticator):
class MixpanelBearerAuthenticator(ApiKeyAuthenticator):
    @property
    def token(self) -> str:
        # class TokenAuthenticatorBase64(TokenAuthenticator):
        #     def __init__(self, token: str):
        #         token = base64.b64encode(token.encode("utf8")).decode("utf8")
        #         super().__init__(token=token, auth_method="Basic")
        token = self.token_provider.get_token()
        token = base64.b64encode(token.encode("utf8")).decode("utf8")
        return f"Basic {token}"

@dataclass
class MixpanelHttpRequester(HttpRequester):
    def get_url_base(self) -> str:
        """
        REGION: url
        US    : https://mixpanel.com/api/2.0/
        EU    : https://EU.mixpanel.com/api/2.0/
        """
        url_base = super().get_url_base().replace("US.", "")
        return url_base

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        project_id = self.config.get('credentials', {}).get('project_id')
        return {'project_id': project_id} if project_id else {}

class AnnotationsHttpRequester(MixpanelHttpRequester):

    def get_url_base(self) -> str:
        """
        REGION: url
        app/projects/{{ project_id }}/annotations
        """
        project_id = self.config.get('credentials', {}).get('project_id', "")
        project_part = f"{project_id}/" if project_id else ""
        return f"{super().get_url_base()}{project_part}"

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {}

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


class EngageDefaultPaginator(DefaultPaginator):
    ...


from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement


class EngagePaginationStrategy(PageIncrement):
    """
    Page increment strategy with subpages for the `items` stream.

    From the `items` documentation https://developer.monday.com/api-reference/docs/items:
        Please note that you cannot return more than 100 items per query when using items at the root.
        To adjust your query, try only returning items on a specific board, nesting items inside a boards query,
        looping through the boards on your account, or querying less than 100 items at a time.

    This pagination strategy supports nested loop through `boards` on the top level and `items` on the second.
    See boards documentation for more details: https://developer.monday.com/api-reference/docs/boards#queries.
    """

    def __post_init__(self, parameters: Mapping[str, Any]):
        # `self._page` corresponds to board page number
        # `self._sub_page` corresponds to item page number within its board
        self.start_from_page = 1
        self._page: Optional[int] = self.start_from_page
        self._sub_page: Optional[int] = self.start_from_page
        self._total: Optional[int] = 0

    def next_page_token(self, response, last_records: List[Mapping[str, Any]]) -> Optional[Tuple[Optional[int], Optional[int]]]:
        """
        Determines page and subpage numbers for the `items` stream

        Attributes:
            response: Contains `boards` and corresponding lists of `items` for each `board`
            last_records: Parsed `items` from the response
        """
        decoded_response = response.json()
        page_number = decoded_response.get("page")
        total = decoded_response.get("total")  # exist only on first page
        if total:
            self._total = total

        if self._total and page_number is not None and self._total > self.page_size * (page_number + 1):
            return {
                "session_id": decoded_response.get("session_id"),
                "page": page_number + 1,
            }
        else:
            self._total = None
            return None
