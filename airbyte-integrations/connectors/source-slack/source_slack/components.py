from dataclasses import dataclass
from typing import Optional
from typing import List, Mapping, Any, Iterable
import requests
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.transformations import RecordTransformation, AddFields
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter


@dataclass
class ChannelMembersExtractor(DpathExtractor):
    """
    Transform response from list of strings to list dicts:
    from: ['aa', 'bb']
    to: [{'member_id': 'aa'}, {{'member_id': 'bb'}]
    """
    def extract_records(self, response: requests.Response) -> List[Record]:
        records = super().extract_records(response)
        return [{'member_id': record} for record in records]


@dataclass
class JoinChannels(RecordTransformation):
    """
    Make 'conversations.join' POST request for every found channel id
    if we are not still a member of such channel
    """

    def transform(
        self,
        record: Record,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> Record:
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

            # WHAT TO DO IF IT FAILS ????????????????????????
            # self.logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Successfully joined channel: {channel_id}")


@dataclass
class ThreadsPartitionRouter(SubstreamPartitionRouter):
    """Overwrite SubstreamPartitionRouter to be able to pass more than one value
    from parent stream to stream_slices
    """
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
        Change behaviour of main stream_slices by adding two values (for channel_id, ts) from parent stream
        (previously it was possible to add only one value)
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

                    empty_parent_slice = True
                    parent_slice = parent_stream_slice

                    for parent_record in parent_stream.read_records(
                        sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                    ):

                        print(parent_record)
                        # Skip non-records (eg AirbyteLogMessage)
                        if isinstance(parent_record, AirbyteMessage):
                            if parent_record.type == Type.RECORD:
                                parent_record = parent_record.record.data
                            else:
                                continue
                        elif isinstance(parent_record, Record):
                            parent_record = parent_record.data

                        empty_parent_slice = False

                        yield {
                            'channel_id': parent_record['channel_id'],
                            'ts': parent_record['ts'],
                            "parent_slice": parent_slice
                        }
                    # If the parent slice contains no records,
                    if empty_parent_slice:
                        yield from []
