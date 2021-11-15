#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, List, Any, Iterable, Optional, Union, MutableMapping, Tuple
import json
import pathlib

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import (
    AirbyteStream,
    SyncMode
)
from airbyte_cdk.sources import AbstractSource
from .plaid_requester import PlaidRequester

CATALOG_PATH = pathlib.Path(__file__).parent / 'catalog.json'
CURSOR_FIELD = 'date'
STATE_START_FIELD = 'start_date'

class SourcePlaid(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            api_requester = PlaidRequester.from_config(**config)
            api_requester.test_connection()
            return True, None
        except Exception as error:
            return False, error

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        plaid_requester = PlaidRequester.from_config(**config)

        catalog_configuration = json.loads(CATALOG_PATH.read_text())
        return [PlaidStream(AirbyteStream(**stream['stream']), plaid_requester) \
                for stream in catalog_configuration['streams']]


class PlaidStream(Stream):
    NAME_TO_PRIMARY_KEY = {
        'transaction': 'transaction_id',
        'balance': 'account_id'
    }

    def __init__(self, stream_config: AirbyteStream, plaid_requester: PlaidRequester):
        self.stream_config = stream_config
        self.plaid_requester = plaid_requester

    @property
    def name(self):
        return self.stream_config.name

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        if SyncMode.incremental in self.stream_config.supported_sync_modes:
            return CURSOR_FIELD
        return []

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.stream_config.json_schema

    @property
    def source_defined_cursor(self) -> bool:
        """
        Return False if the cursor can be configured by the user.
        """
        return True

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self.NAME_TO_PRIMARY_KEY[self.stream_config.name]

    @staticmethod
    def stream_parser_factory(plaid_requester: PlaidRequester, stream_name: str):
        return getattr(plaid_requester, f"{stream_name}_generator")

    def read_records(self, sync_mode: SyncMode,
                     cursor_field: List[str] = None,
                     stream_slice: Mapping[str, Any] = None,
                     stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        plaid_generator_function = self.stream_parser_factory(self.plaid_requester, self.name)
        if sync_mode == SyncMode.incremental:
            plaid_generator = plaid_generator_function(**stream_state)
        else:
            plaid_generator = plaid_generator_function()

        yield from plaid_generator

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        return {STATE_START_FIELD: latest_record[CURSOR_FIELD]}
