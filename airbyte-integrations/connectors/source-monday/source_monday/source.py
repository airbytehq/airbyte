#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class MondayStream(HttpStream, ABC):
    url_base = "https://api.monday.com/v2"
    primary_key = "id"
    page = 1


    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json().get('data', {})
        records = json_response.get(self.name.lower(), [])
        self.page += 1
        if records:
            return {"page": self.page}
    
    def load_schema(self):
        '''
        Load schema from file and make a GraphQL query
        '''
        with open(f'./source_monday/schemas/{self.name.lower()}.json') as f:
            schema_dict = json.load(f)
            schema = schema_dict['stream']['json_schema']['properties']
            graphql_schema = []
            for col in schema:
                if 'properties' in schema[col]:
                    nested_ids = ','.join(schema[col]['properties'])
                    graphql_schema.append(f'{col}{{{nested_ids}}}')
                else:
                    graphql_schema.append(col)
        return ','.join(graphql_schema)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        graphql_params = {}
        if next_page_token:
            graphql_params.update(next_page_token)

        graphql_query = ','.join([f'{k}:{v}' for k,v in graphql_params.items()])

        params = {
            'query': f"query {{ {self.name.lower()} ({graphql_query}) {{ {self.load_schema()} }} }}"
        }
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json().get('data', {})
        records = json_response.get(self.name.lower(), [])
        yield from records
    
    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return ''

class Items(MondayStream):
    """
    API Documentation: https://api.developer.monday.com/docs/items-queries
    """

class Boards(MondayStream):
    """
    API Documentation: https://api.developer.monday.com/docs/groups-queries#groups-queries
    """

# Source
class SourceMonday(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = 'https://api.monday.com/v2'
        params = {"query": "{boards(limit:1){id name}}"}
        auth = TokenAuthenticator(config['api_token']).get_auth_header()
        try:
            response = requests.post(url, params=params, headers=auth)
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config['api_token'])
        return [
            Items(authenticator=auth),
            Boards(authenticator=auth)
        ]
