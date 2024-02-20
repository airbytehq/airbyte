import dpath.util
from dataclasses import dataclass
from typing import Optional
from typing import List, Mapping, Any, Iterable
import requests
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.declarative.transformations import RecordTransformation, AddFields
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
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


@dataclass
class ThreadsPartitionRouter(SubstreamPartitionRouter):

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {
            'channel': stream_slice['channel_id'],
            'ts': stream_slice['ts'],
        }

    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Iterate over each parent stream's record and create a StreamSlice for each record.

        For each stream, iterate over its stream_slices.
        For each stream slice, iterate over each record.
        yield a stream slice for each such records.

        If a parent slice contains no record, emit a slice with parent_record=None.

        The template string can interpolate the following values:
        - parent_stream_slice: mapping representing the parent's stream slice
        - parent_record: mapping representing the parent record
        - parent_stream_name: string representing the parent stream name
        """
        if not self.parent_stream_configs:
            yield from []
        else:
            for parent_stream_config in self.parent_stream_configs:
                parent_stream = parent_stream_config.stream
                parent_field = parent_stream_config.parent_key.eval(self.config)
                stream_state_field = parent_stream_config.partition_field.eval(self.config)
                for parent_stream_slice in parent_stream.stream_slices(
                    sync_mode=SyncMode.full_refresh, cursor_field=None, stream_state=None
                ):
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                    print("parent_stream_slice")
                    print(parent_stream_slice)
                    empty_parent_slice = True
                    parent_slice = parent_stream_slice

                    for parent_record in parent_stream.read_records(
                        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                    ):
                        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        print("parent_record")
                        print(parent_record)
                        # Skip non-records (eg AirbyteLogMessage)
                        if isinstance(parent_record, AirbyteMessage):
                            if parent_record.type == Type.RECORD:
                                parent_record = parent_record.record.data
                            else:
                                continue
                        elif isinstance(parent_record, Record):
                            parent_record = parent_record.data
                        # try:
                        #     stream_state_value = dpath.util.get(parent_record, parent_field)
                        # except KeyError:
                        #     pass
                        # else:
                        empty_parent_slice = False
                        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        print(parent_record)
                        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        yield {
                            'channel_id': parent_record['channel_id'],
                            'ts': parent_record['ts'],
                            "parent_slice": parent_slice
                        }
                    # If the parent slice contains no records,
                    if empty_parent_slice:
                        yield from []
