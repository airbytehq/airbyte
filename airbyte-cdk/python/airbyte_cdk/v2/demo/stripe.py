from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Mapping, Any, Iterable, AsyncIterable

import aiohttp
from airbyte_protocol.models import ConfiguredAirbyteCatalog, Type

from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.v2 import StateType
from airbyte_cdk.v2.concurrency import HttpRequestDescriptor, HttpPartitionDescriptor, PartitionedStream, PartitionType, \
    ConcurrentStreamGroup, ConcurrencyPolicy
from airbyte_cdk.v2.concurrency.http import GetRequest, AiohttpRequester, Paginator, ResponseType
from airbyte_cdk.v2.state import DatetimePartitionDescriptor, DatetimePartitionGenerator, DatetimeState, StateManager, DatetimeStateManager

STRIPE_API_URL = "https://api.stripe.com/v1"
STRIPE_SECRET_KEY = open("/Users/sherif/stripe-key", "r").read()
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
                part.partition_id,
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
    async def parse_response(self, response: aiohttp.ClientResponse) -> AsyncIterable[StreamData]:
        response_json = await response.json()
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


class StripePaginator(Paginator):
    def get_next_page_info(self, response: ResponseType) -> HttpRequestDescriptor:
        # big TODO
        return HttpRequestDescriptor(None, None, None)


concurrency_factor = 6
stream_group = ConcurrentStreamGroup(
    AiohttpRequester(StripePaginator()),
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
