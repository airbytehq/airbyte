#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from datetime import datetime, timedelta
from airbyte_cdk.sources.streams.http.auth import NoAuth
from airbyte_cdk.models import SyncMode
from time import sleep
import base64
import xmltodict

class EMilleniumBase(HttpStream):

    url_base = "http://179.124.195.19:6017/api/"

    def __init__(
        self, 
        config: Mapping[str, Any],
        **kwargs
    ):
        super().__init__()
        self.username = config['username']
        self.password = config['password']
        self.merchant = config['merchant']
        self.start_offset = 0
        self.end_offset = 100
        self.end_of_records = False

        self.token = self.encode_credentials()

    def encode_credentials(self):
        authorization_string = f"{self.username}:{self.password}"
        authorization_bytes = authorization_string.encode('ascii')

        return  base64.b64encode(authorization_bytes).decode("utf-8") 

    
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        headers = {
            "Authorization": f"Basic {self.token}",
            "WTS-LicenseType": 'prat_api'
        }

        return headers

    def set_initial_date(self, stream_state):
        inital_date = self.start_date 
        if self.cursor_field in stream_state.keys():
            inital_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
        
        return datetime.strftime(inital_date, '%Y-%m-%d')

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        current_date_datetime = datetime.strptime(self.current_date, '%Y-%m-%d')

        if current_date_datetime.date() > datetime.now().date():
            return None 
        
        current_date_datetime = current_date_datetime + timedelta(days = 1)

        self.current_date = datetime.strftime(current_date_datetime, '%Y-%m-%d')

        return self.current_date

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_record_date = datetime.fromtimestamp(int(latest_record['data'][self.record_date_field].split('(')[1].split('-')[0])/1000)

        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()

        item_list = []

        for item in response_json[self.record_list_name]:
            item_json = {
                "data":item,
                "merchant": self.merchant.upper(),
                "source": "BR_EMILLENIUM",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": item[self.record_primary_key],
                "timeline": "historic",
                "created_at": datetime.fromtimestamp(int(item[self.record_date_field].split('(')[1].split('-')[0])/1000).strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False
            }

            item_list.append(item_json)
            
        return item_list


class Listafaturamentos(EMilleniumBase):

    cursor_field = "data_nota_fiscal"
    primary_key = "data_nota_fiscal"

    endpoint_name = 'MILLENIUM_ECO!PROMEX.PEDIDO_VENDA.LISTAFATURAMENTOS'
    record_list_name = 'value'
    record_primary_key = 'cod_pedidov'
    record_key_name =  'nota_fiscal'
    record_date_field = 'data_hora'

    def __init__(
        self, 
        config: Mapping[str, Any], 
        start_date: datetime,
        **kwargs
    ):
        super().__init__(config)

        self.start_date = start_date

        self._cursor_value = None

        self.first_run = True

    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        
        if self.first_run == True:
            self.current_date = self.set_initial_date(stream_state)
            self.first_run = False

        path = f"{self.endpoint_name}?data_atualizacao={self.current_date}&$format=json"
        
        logger.info(path)
        
        return path
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()

        item_list = []

        for item in response_json[self.record_list_name]:
            item_json = {
                "data":item,
                "data_xml": xmltodict.parse(item['xml'].strip()),
                "merchant": self.merchant.upper(),
                "source": "BR_EMILLENIUM",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": item[self.record_primary_key],
                "timeline": "historic",
                "created_at": datetime.fromtimestamp(int(item[self.record_date_field].split('(')[1].split('-')[0])/1000).strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False
            }

            item_list.append(item_json)
            
        return item_list

class Listapedidos(EMilleniumBase):

    cursor_field = "data_pedidos"
    primary_key = "data_pedidos"

    endpoint_name = 'millenium_eco/pedido_venda/listapedidos'
    record_list_name = 'value'
    record_primary_key = 'cod_pedidov'
    record_key_name =  'nota_fiscal'
    record_date_field = 'data_emissao'

    def __init__(
        self, 
        config: Mapping[str, Any], 
        start_date: datetime,
        **kwargs
    ):
        super().__init__(config)

        self.start_date = start_date

        self._cursor_value = None

        self.first_run = True

    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        
        if self.first_run == True:
            self.current_date = self.set_initial_date(stream_state)
            self.first_run = False

        path = f"{self.endpoint_name}?aprovado=true&data_emissao={self.current_date}&efetuado=true&$format=json"
        
        logger.info(path)
        
        return path
    
class SourceEMillenium(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # auth = NoAuth()
            # start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')
            # stream = Listapedidos(authenticator=auth, config=config, start_date=start_date)
            # records = stream.read_records(sync_mode=SyncMode.full_refresh)
            # next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()
        start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')

        return [
            Listafaturamentos(authenticator=auth, config=config, start_date=start_date),
            Listapedidos(authenticator=auth, config=config, start_date=start_date)
        ]
