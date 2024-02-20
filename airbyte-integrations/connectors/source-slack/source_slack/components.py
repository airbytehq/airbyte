from dataclasses import dataclass
from typing import Optional
from typing import List, Mapping, Any, Iterable
import requests
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.declarative.transformations import RecordTransformation, AddFields
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import StreamData


@dataclass
class ChannelMembersExtractor(DpathExtractor):
    """
    Record extractor that extracts record of the form from activity logs stream:
    """
    def extract_records(self, response: requests.Response) -> List[Record]:
        records = super().extract_records(response)
        return [{'member_id': record} for record in records]


@dataclass
class JoinChannels(RecordTransformation):
    """
    Implementations of this class define transformations that can be applied to records of a stream.
    """

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        """ sdf """
        print(f"++++++++++CHECK {record['id']} ++++++++++++++++++++++++++++++++++++++++")
        # The `is_member` property indicates whether or not the API Bot is already assigned / joined to the channel.
        # https://api.slack.com/types/conversation#booleans
        channel_id = record.get('id')
        if config.get('join_channels') and not record.get("is_member"):
            response = requests.post(
                url='https://slack.com/api/conversations.join',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {config["api_token"]}'
                },
                params={'channel': channel_id}
            )
            print(response.json())

        # self.logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Successfully joined channel: {channel_id}")

