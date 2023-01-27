#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from airbyte_cdk.models import SyncMode
from datetime import datetime, timedelta


class BlingBase(HttpStream):
    '''
    Bling base class with default ingestion methods

    API Doc: https://ajuda.bling.com.br/hc/pt-br/categories/360002186394-API-para-Desenvolvedores

    Use the logger.info(str) function for debugging
    '''

    url_base = "https://bling.com.br/Api/v2/"

    def __init__(
        self, 
        config: Mapping[str, Any],
        **kwargs
    ):
        '''
        The following parameters must be present in all streams:
            endpoint_name: Bling API endpoint name   
            record_list_name: Return the name of the object list containing the data            
            record_key_name: The root key of a JSON object          
            record_primary_key: Data primary key
        '''
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

        return f"{self.endpoint_name}/page={self.page}/json/"  
    
    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ):
        '''
        Adds necessary request parameters
        '''

        params = {
            "apikey":self.api_key
        }

        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        '''
        Responsible for updating the page parameter\n

        After each response, this function is called to update the page parameter \n
        In Bling's case, there is no token, only a 'page' parameter that is set on the path function. \n
        When this function returns None, the ingestion process is stopped
        '''

        if self.end_of_pages == True:
            return None

        self.page += 1

        return self.page
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        '''
        Responsible for parsing and creating data records

        Bling endpoints work with a 'page' parameter that sets which data will be read \n
        When a page without data is reached, it returns on the response body a 'erros' key \n
        When the record_list_name is not available on the response, the 'end_of_pages' variable is set to NULL in order to
        'next_page_token' finish the ingestion process \n
        Otherwise, the JSON with all necessary attributes is built and will be ingested
        '''

        response_json = response.json()

        if self.record_list_name not in response_json['retorno'].keys():
            self.end_of_pages = True
            return []

        item_list = []

        for item in response_json['retorno'][self.record_list_name][:1]:
            item_json = {
                "data":item[self.record_key_name],
                "merchant": self.merchant.upper(),
                "source": "BR_BLING",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": item[self.record_key_name][self.record_primary_key],
                "timeline": "historic",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False
            }

            item_list.append(item_json)
            
        return item_list


class Produtos(BlingBase):
    '''
    Products endpoint for Bling

    API Doc: https://ajuda.bling.com.br/hc/pt-br/articles/360046422714-GET-produtos

    Only full-refresh ingestion is available hence we don't have a date parameter on the API
    '''

    #Always set primary_key to None for FULL ingestions
    primary_key = None

    endpoint_name = 'produtos'
    record_list_name = 'produtos'
    record_key_name = 'produto'
    record_primary_key = 'id'

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

class IncrementalBlingBase(BlingBase):
    '''
    Incremental Bling base class

    Two sync modes are available:
        full-refresh: Ingests all data based on Start Date config
        incremental: On the first run ingests like a full-refresh, in the following runs it will ingest
        from the last date ingested

    For historical reprocessing, just change the sync mode to "full-refresh | append", and after running the process, change
    it again to incremental
    '''


    def __init__(
        self, 
        config: Mapping[str, Any], 
        start_date: datetime,
        **kwargs
    ):
        '''
        The following parameters must be present in all incremental streams:
            cursor_field: Airbyte reference date field for incremental ingestions
            primary_key: Same use as cursor_field
            record_date_field: Date field name inside the JSON object. It will be used
            to check which was the last date ingested
            api_date_filter_field: API date filter name
        '''
        super().__init__(config)

        self.start_date = start_date

    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        '''
        Returns the path to be used in the next ingestion interaction \n

        Runs after the 'next_page_token' function (Only after the first run) \n
        Overrides BaseBling path in order to add dataEmissao filter \n

        Checks if a value is available on stream_state dict. After the first run,
        stream_state will have a key with cursor_field name with last ingested date
        as value

        '''


        start_ingestion_date = self.start_date
        if self.cursor_field in stream_state.keys():
            start_ingestion_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT00:00:00') - timedelta(days=15)
        
        return f"{self.endpoint_name}/page={self.page}/json/?filters={self.api_date_filter_field}[{datetime.strftime(start_ingestion_date, '%d/%m/%Y')} TO {datetime.strftime(datetime.now(), '%d/%m/%Y')}]"  
    
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        
        latest_record_date = datetime.strptime(latest_record['data'][self.record_date_field], '%Y-%m-%d')

        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT00:00:00')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}

class Pedidos(IncrementalBlingBase):
    '''
    Pedidos endpoint for Bling

    API Doc: https://ajuda.bling.com.br/hc/pt-br/articles/360046424094-GET-pedidos
    '''

    cursor_field = "data_pedido"
    primary_key = "data_pedido"

    endpoint_name = 'pedidos'
    record_list_name = 'pedidos'
    record_key_name = 'pedido'
    record_primary_key = 'numero'
    record_date_field = 'data'
    api_date_filter_field = 'dataEmissao'

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
        start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')

        return [
            Produtos(authenticator=auth, config=config),
            Pedidos(authenticator=auth, config=config, start_date=start_date)
        ]