#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
import math
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Dict

import requests
from airbyte_cdk.models import AirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from source_gridly.helpers import Helpers


# Basic full refresh stream
class GridlyStream(HttpStream, ABC):
    url_base = "https://api.gridly.com/v1/"
    primary_key = "id"
    current_page = 0
    limit = 100

    def __init__(self, view_id: str, view_name: str, schema: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.view_id = view_id
        self.view_name = view_name
        self.schema = schema

    @property
    def name(self):
        return self.view_name

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.schema

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        total_count = response.headers.get('x-total-count')
        total_page = math.ceil(int(total_count) / self.limit)

        self.logger.info('Total page: ' + str(total_page))

        if self.current_page >= total_page:
            self.logger.info('No more page to load ' + str(self.current_page))
            return None

        page_token = {'offset': self.current_page * self.limit, 'limit': self.limit}
        self.current_page += 1

        return page_token

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token is None:
            return {}

        offset = next_page_token.get('offset')
        limit = next_page_token.get('limit')

        page = '{"offset":' + str(offset) + ',"limit":' + str(limit) + '}'

        self.logger.info('Fetching page: ' + page)

        return {'page': page}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json()
        if isinstance(records, list):
            for record in records:
                yield Helpers.transform_record(record, self.schema)
        else:
            Exception(f"Unsupported type of response data for stream {self.name}")

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"views/{self.view_id}/records"


# Source
class SourceGridly(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        api_key = config.get('api_key')
        view_id = config.get('view_id')
        auth = TokenAuthenticator(auth_method='ApiKey', token=api_key)

        logger.info(f"Checking connection on view {view_id}")
        Helpers.get_view(auth=auth, view_id=view_id)

        return True, None

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        api_key = config.get('api_key')
        view_id = config.get('view_id')
        auth = TokenAuthenticator(auth_method='ApiKey', token=api_key)

        logger.info(f"Running discovery on view {view_id}")
        view = Helpers.get_view(auth=auth, view_id=view_id)
        streams = [Helpers.get_airbyte_stream(view)]

        return AirbyteCatalog(streams=streams)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        api_key = config.get('api_key')
        view_id = config.get('view_id')
        auth = TokenAuthenticator(auth_method='ApiKey', token=api_key)
        view = Helpers.get_view(auth=auth, view_id=view_id)
        schema = Helpers.get_json_schema(view)
        view_name = view.get('name')

        return [GridlyStream(view_id=view_id, view_name=view_name, schema=schema, authenticator=auth)]
