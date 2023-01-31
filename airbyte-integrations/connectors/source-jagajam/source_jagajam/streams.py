import json
from abc import ABC
from datetime import datetime, timedelta
from pprint import pprint
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpSubStream

from .fields import COMMUNITIES_FIELDS
from .base_stream import JagajamStream


class PaginatedStream(ABC):
    items_per_page_count = 1000

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pagination_data = response.json()['pagination']
        if pagination_data['next_page']:
            return {'next_page': pagination_data['next_page']}

    def request_params(
        self,
        next_page_token: Mapping[str, Any] = None,
        *args,
        **kwargs
    ) -> MutableMapping[str, Any]:
        return {
            "page": next_page_token.get('next_page') if next_page_token else 1,
            "per_page": PaginatedStream.items_per_page_count,
        }


class Communities(JagajamStream):
    use_cache = True
    primary_key = 'cid'

    def path(self, *args, **kwargs) -> str:
        return 'analytics'

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update({'fields': ','.join(COMMUNITIES_FIELDS)})
        return params


class DateRangeStream(JagajamStream, ABC):
    DATE_FORMAT = '%d.%m.%Y'

    def __init__(
        self,
        auth_token: str,
        date_from: datetime,
        date_to: datetime,
        date_granuilarity: str,
        chunks_config: Mapping[str, Any],
        available_communities: list[Mapping[str, Any]],
        client_name: str = None,
        product_name: str = None,
        custom_constants: Mapping[str, Any] = {},
    ):
        JagajamStream.__init__(
            self,
            auth_token=auth_token,
            client_name=client_name,
            product_name=product_name,
            custom_constants=custom_constants
        )
        self.date_from = date_from
        self.date_to = date_to
        self.available_communities = available_communities
        self.date_granuilarity = date_granuilarity
        self.should_split_into_chunks = chunks_config['chunk_mode_type'] == 'split_into_chunks'
        self.chunk_size_in_days = chunks_config.get('chunk_size_in_days')

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update(
            {
                'date1s': datetime.strftime(
                    stream_slice['date_from'],
                    DateRangeStream.DATE_FORMAT
                ),
                'date1f': datetime.strftime(
                    stream_slice['date_to'],
                    DateRangeStream.DATE_FORMAT
                ),
                "group": self.date_granuilarity
            }
        )
        return params

    def day_chunks(self, date_from: datetime, date_to: datetime) -> Iterable[datetime]:
        cursor = date_from
        delta = timedelta(days=self.chunk_size_in_days - 1)
        while cursor < date_to:
            if cursor + delta > date_to:
                yield {'date_from': cursor, 'date_to': date_to}
                return
            yield {'date_from': cursor, 'date_to': cursor + delta}
            cursor = cursor + delta + timedelta(days=1)

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        if self.should_split_into_chunks:
            day_chunks = list(self.day_chunks(self.date_from, self.date_to))
            pprint(day_chunks)
            yield from day_chunks
        else:
            yield from [{'date_from': self.date_from, 'date_to': self.date_to}]


class CommunitiesDetailsStream(ABC):
    def __init__(self, available_communities: list[Mapping[str, Any]]):
        self.available_communities = available_communities

    def request_params(
        self,
        stream_slice: Mapping[str, Any] = None,
        *args,
        **kwargs
    ) -> MutableMapping[str, Any]:
        return {
            'items': json.dumps(
                [{"type": "community", "cid": stream_slice['community_cid']}]
            )
        }

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [
            {'community_cid': community['cid']}
            for community in self.available_communities
        ]


class DateRangeCommunitiesDetailsStream(DateRangeStream, CommunitiesDetailsStream, ABC):
    primary_key = ['date', 'community_cid']

    def __init__(
        self,
        auth_token: str,
        date_from: datetime,
        date_to: datetime,
        date_granuilarity: str,
        available_communities: list[Mapping[str, Any]],
        chunks_config: Mapping[str, Any],
        client_name: str = None,
        product_name: str = None,
        custom_constants: Mapping[str, Any] = {}
    ):
        DateRangeStream.__init__(
            self,
            auth_token=auth_token,
            date_from=date_from,
            date_to=date_to,
            available_communities=available_communities,
            date_granuilarity=date_granuilarity,
            chunks_config=chunks_config,
            client_name=client_name,
            product_name=product_name,
            custom_constants=custom_constants,
        )
        CommunitiesDetailsStream.__init__(
            self, available_communities=available_communities)

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            **DateRangeStream.request_params(
                self,
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token
            ),
            **CommunitiesDetailsStream.request_params(
                self,
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token
            )
        }

    def parse_response(
        self,
        response: requests.Response,
        stream_slice: Mapping[str, Any] = None,
        *args,
        **kwargs
    ) -> Iterable[Mapping]:
        for record in response.json()['data']['series']:
            yield self.add_constants_to_record({
                "date": record['point']['range_a']['name'],
                'community_cid': stream_slice['community_cid'],
                **record['params']
            })

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for community_slice in CommunitiesDetailsStream.stream_slices(self, *args, **kwargs):
            community_details = next(
                filter(
                    lambda community: community['cid'] == community_slice['community_cid'],
                    self.available_communities
                )
            )
            community_min_date = datetime.strptime(
                community_details['access_retrospective'], '%Y-%m-%dT%H:%M:%S.%fZ'
            )
            date_from = self.date_from
            if community_min_date > self.date_from:
                self.logger.info(
                    f'Min date for {community_details["cid"]} community '
                    f'- {str(community_min_date.date())}. Use this date as date_from'
                )
                date_from = community_min_date
            if self.should_split_into_chunks:
                for date_range_slice in self.day_chunks(date_from, self.date_to):
                    yield {**date_range_slice, "community_cid": community_slice['community_cid']}
            else:
                yield from [{
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    "community_cid": community_slice['community_cid']
                }]


class PaginatedDateRangeCommunitiesDetailsStream(
    PaginatedStream,
    DateRangeCommunitiesDetailsStream,
    ABC
):
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            **DateRangeCommunitiesDetailsStream.request_params(
                self,
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token
            ),
            **PaginatedStream.request_params(
                self,
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token
            )
        }


class ReachCount(DateRangeCommunitiesDetailsStream):
    def path(self, *args, **kwargs) -> str:
        return 'charts/reach_count/'


class UsersCount(DateRangeCommunitiesDetailsStream):
    def path(self, *args, **kwargs) -> str:
        return 'charts/users_count'


class Benchmarks(DateRangeCommunitiesDetailsStream):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.should_split_into_chunks = True
        self.chunk_size_in_days = 1

    def path(self, *args, **kwargs) -> str:
        return 'charts/benchmarks'

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> Iterable[Mapping]:
        for record in response.json()['data']['series']:
            yield self.add_constants_to_record({
                "date": record['point']['label']['date1s'],
                'community_cid': stream_slice['community_cid'],
                **record['params']
            })


class Posts(PaginatedDateRangeCommunitiesDetailsStream):
    def path(self, *args, **kwargs) -> str:
        return 'tables/posts'

    def parse_response(self, response: requests.Response, *args, **kwargs) -> Iterable[Mapping]:
        yield from map(self.add_constants_to_record, response.json()['data']['a'])
