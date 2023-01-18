#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from airbyte_cdk.models import SyncMode
from datetime import datetime


class Produtos(HttpStream):
    '''
    Products endpoint for Bling

    API Doc: https://ajuda.bling.com.br/hc/pt-br/articles/360046422714-GET-produtos

    Only full-refresh ingestion is available hence we don't have a date parameter on the API
    '''

    url_base = "https://bling.com.br/Api/v2/produtos/json/"

    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config['api_key']
        self.merchant = config['merchant']
        self.page = 1
        self.end_of_pages = False

    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        '''
        Returns the path to be used in the next ingestion interaction \n

        Runs after the 'next_page_token' function (Only after the first run)
        '''

        return f"produtos/page={self.page}/json/"  

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ):
        '''
        Adds necessary request parameters \n

        'estoque' and 'imagem' parameters should be set to 'S' to retrieve all available information\n
        API authentication is done by the 'apikey' parameter
        '''

        params = {
            "apikey":self.api_key, 
            "estoque":"S",
            "imagem":"S"
        }
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        '''
        Responsible for updating the page parameter\n

        After each response, this function is called to update the page parameter \n
        In Bling's case, there is no token, only a 'page' parameter that is set on the path function. \n
        When this function returns None, the ingestion process is stopped
        '''

        if self.end_of_pages == True: return None

        self.page += 1

        return self.page

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        '''
        Responsible for parsing and creating data records

        Bling Products endpoint works with a 'page' parameter that sets which data will be read \n
        When a page without data is reached, it returns on the response body a 'erros' key \n
        When 'produtos' is not available on the response, the 'end_of_pages' variable is set to NULL in order to
        'next_page_token' finish the ingestion process \n
        Otherwise, the JSON with all necessary attributes is built and will be ingested
        '''

        response_json = response.json()

        if 'produtos' not in response_json['retorno'].keys():
            self.end_of_pages = True
            return []

        produtos = []

        for item in response_json['retorno']['produtos']:
            produto = {
                "data":item['produto'],
                "merchant": self.merchant.upper(),
                "source": "BR_BLING",
                "type": f"{self.merchant.lower()}_invoice",
                "id": item['produto']['id'],
                "timeline": "historic",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False
            }

            produtos.append(produto)
            
        return produtos


class SourceBling(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = NoAuth()
            stream = Produtos(authenticator=auth, config=config)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()  
        return [Produtos(authenticator=auth, config=config)]


# # Basic incremental stream
# class IncrementalBlingStream(BlingStream, ABC):
#     """
#     TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
#          if you do not need to implement incremental sync for any streams, remove this class.
#     """

#     # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
#     state_checkpoint_interval = None

#     @property
#     def cursor_field(self) -> str:
#         """
#         TODO
#         Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
#         usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

#         :return str: The name of the cursor field.
#         """
#         return []

#     def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
#         """
#         Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
#         the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
#         """
#         return {}
