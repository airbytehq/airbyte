from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Mapping, Any, Iterable, AsyncIterable, Optional, Union, List

import aiohttp
import requests
from airbyte_protocol.models import ConfiguredAirbyteCatalog, Type, SyncMode

from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.v2.concurrency.concurrency_policy import ConcurrencyPolicy
from airbyte_cdk.v2.concurrency.partition_descriptors import PartitionDescriptor
from airbyte_cdk.v2.concurrency.partitioned_stream import PartitionedStream
from airbyte_cdk.v2.concurrency.stream_group import ConcurrentStreamGroup, PartitionType
from airbyte_cdk.v2.state_obj import StateType
from airbyte_cdk.v2.concurrency.http import GetRequest, AiohttpRequester, Paginator, ResponseType, HttpPartitionDescriptor, \
    HttpRequestDescriptor
from airbyte_cdk.v2.state import DatetimePartitionDescriptor, DatetimePartitionGenerator, DatetimeState, StateManager, DatetimeStateManager
import json

STRIPE_API_URL = "https://api.stripe.com/v1"
STRIPE_SECRET_KEY = json.loads(open("/Users/alex/code/tools/airbyte-integrations/connectors/source-stripe/secrets/config.json", "r").read())["client_secret"]
STRIPE_ACCOUNT_NUMBER = "acct_1G9HZLIEn5WyEQxn"


@dataclass
class StripePartitionDescriptor(DatetimePartitionDescriptor, HttpPartitionDescriptor):
    pass


class StripePartitionGenerator(DatetimePartitionGenerator):
    def __init__(self, endpoint: str, account_id: str, start: datetime, secret_key: str):
        super().__init__(start, timedelta(days=30))
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.account_id = account_id

    def generate_partitions(
            self,
            **kwargs
    ) -> Iterable[DatetimePartitionDescriptor]:
        for part in super().generate_partitions(**kwargs):
            yield StripePartitionDescriptor(
                part.metadata,
                self._generate_request_descriptor(part),
                part.start_datetime,
                part.end_datetime
            )

    def _generate_request_descriptor(self, datetime_partition: DatetimePartitionDescriptor) -> HttpRequestDescriptor:
        return GetRequest(
            base_url=STRIPE_API_URL,
            path=self.endpoint,
            request_parameters={
                'created[gte]': int(datetime_partition.start_datetime.timestamp()),
                'created[lte]': int(datetime_partition.end_datetime.timestamp()),
            },
            headers={'Stripe-Account': self.account_id, "Authorization": f"Bearer {self.secret_key}"}
        )


class StripeStream(PartitionedStream):
    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None,
                     stream_state: Mapping[str, Any] = None) -> Iterable[StreamData]:
        pass

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        pass

    def generate_partitions(self, stream_state, catalog) -> Iterable[PartitionDescriptor]:
        return self.get_partition_descriptors(stream_state, catalog)

    async def parse_response_async(self, aio_response: aiohttp.ClientResponse):
        response = requests.Response()
        response.status_code = aio_response.status
        response.request = aio_response.request_info
        response._content = bytes(json.dumps(await aio_response.json()), 'utf-8')
        return response

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[StreamData]:
        response_json = response.json()
        if isinstance(response_json, Mapping):
            for record in response_json.get('data', []):
                yield record
        else:
            raise Exception(f"Unexpected response format: {response}")
        pass

    def __init__(self, name: str):
        super().__init__(DatetimeStateManager())
        self.name = name
        self.start_date = datetime(2022, 1, 1)

    def get_partition_descriptors(self, stream_state: StateType, catalog: ConfiguredAirbyteCatalog) -> Iterable[PartitionType]:
        yield from StripePartitionGenerator(
            f"/{self.name}",
            STRIPE_ACCOUNT_NUMBER,
            self.start_date,
            STRIPE_SECRET_KEY
        ).generate_partitions()

    async def read_partition(self, configured_catalog: ConfiguredAirbyteCatalog, partition: PartitionType):
        raise Exception("not implemented")
        pass

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value



class StripePaginator(Paginator):
    def get_next_page_info(self, response: ResponseType) -> HttpRequestDescriptor:
        # big TODO
        return HttpRequestDescriptor(None, None, None)


concurrency_factor = 6
stream_group = ConcurrentStreamGroup(
    AiohttpRequester(),
    ConcurrencyPolicy(max_concurrent_requests=concurrency_factor),
    [
        StripeStream("customers"),
        StripeStream("charges"),
        StripeStream("balance_transactions"),
        StripeStream("products"),
    ]
)
t0 = datetime.now()
for record in stream_group.read_all({}, None, None):
    print(record)
print(f"Runtime with {concurrency_factor} concurrent workers: {datetime.now() - t0} seconds")
