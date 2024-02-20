from dataclasses import dataclass
from typing import Optional
from typing import List, Mapping, Any
import requests
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.declarative.transformations import RecordTransformation, AddFields
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type

@dataclass
class ChannelMembersExtractor(DpathExtractor):
    """
    Record extractor that extracts record of the form from activity logs stream:
    """
    def extract_records(self, response: requests.Response) -> List[Record]:
        records = super().extract_records(response)
        return [{'member_id': record} for record in records]

# class ChannelsRecordSelector(RecordSelector):
#     def select_records(
#         self,
#         response: requests.Response,
#         stream_state: StreamState,
#         records_schema: Mapping[str, Any],
#         stream_slice: Optional[StreamSlice] = None,
#         next_page_token: Optional[Mapping[str, Any]] = None,
#     ) -> List[Record]:
#         records = super().select_records(response, stream_state, records_schema, stream_slice, next_page_token)
#         print(records)
#         return records


@dataclass
class JoinChannels(RecordTransformation):
    """
    Implementations of this class define transformations that can be applied to records of a stream.
    """
    join_stream: Stream
    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
        """ sdf """
        if config.get('join_channels') and not record.get("is_member"):
            print(f"++++++++++add {record['id']} ++++++++++++++++++++++++++++++++++++++++")
            self.join_stream.channel_id = record['id']

            for parent_record in self.join_stream.read_records(
                    sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=[], stream_state=None
            ):
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print(parent_record)
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++")

