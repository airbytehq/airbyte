#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import requests
import xmltodict
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from datetime import datetime, timedelta
from airbyte_cdk.sources.streams.http.auth import NoAuth
from airbyte_cdk.models import SyncMode
from time import sleep


class ViaBase(HttpStream):
    
    url_base = ""
    
    def __init__(
        self, 
        config: Mapping[str, Any],
        **kwargs
    ):
        super().__init__()
        self.email= config['email']
        self.password = config['password']
        self.merchant = config['merchant']
        self.url_merchant = config['url_merchant']
        self.end_of_records = False
        self.page=0
        self.token = self.get_token()
        self._cursor_value = None

        # Início data inicial e final
        self.start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')
        self.end_date = datetime.strptime(config['end_date'], '%d/%m/%Y') if 'end_date' in config else datetime.now()
        self.end_date = self.end_date + timedelta(days=15) # Adiciona 15 dia para incluir a data final
        # Fim data inicial e final
    
    

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        headers = {
            "authorization": self.token
            
        }
        self.headers=headers   
        return headers
    
    def get_token(
            self
            
    ):

        response = requests.post(self.url_merchant+"/user/signin/local",
                                 json={"email": self.email,"password": self.password})
        logger.info(response.url)
        return response.json()["token"]
    
    
        
    def path(
        self,
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
        
    ) -> str:
        
        start_ingestion_date = self.start_date
        if self.cursor_field in stream_state.keys():
            start_ingestion_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')


        # Início data inicial e final
        start_date_str = start_ingestion_date.strftime("%Y-%m-%d")
        end_date_str = self.end_date.strftime("%Y-%m-%d")

        return f"{self.url_merchant}/orders?dateFrom={start_date_str}&dateTo={end_date_str}&Page={self.page}"
        
        #return f"{self.url_merchant}/orders?dateFrom=2022-04-28&Page={self.page}"
        # Fim data inicial e final
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        if self.end_of_records == True:
            return None

        self.page+=1

        return self.page
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()
        
        if len(response_json) == 0:
            self.end_of_records = True
            return []

        item_list = []

        for item in response_json:
            item_json = {
                "data":item,
                "merchant": self.merchant.upper(),
                "source": "BR_VIA",
                "type": f"{self.merchant.lower()}_order",
                "id": item[self.record_primary_key],
                "timeline": "historic",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False,
                "data_xml": self.get_data(item['IDOrder'])
                
                }

            item_list.append(item_json)
            
        return item_list
    

    
    
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        #logger.info(latest_record['data'])
        latest_record_date = datetime.strptime(latest_record['data'][self.record_date_field], '%Y-%m-%dT%H:%M:%S.000Z')

        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}

class Orders(ViaBase):
    endpoint_name = 'orders'
    record_primary_key = 'IDOrder'
    primary_key = 'data_order'
    cursor_field = 'data_order'
    record_date_field = 'Recordtimestamp'

    def get_data(self, id_order):
        params = {
            "IDOrder": id_order,
            "View": 2
        }

        response = requests.post(self.url_merchant+"/orders/invoice-xml",
                                 json=params, headers=self.headers)
        xml = response.json()
        json_response = {"data_xml": xml}
        logger.info(id_order)
        if "xmlcontent" in xml.keys():
            return xmltodict.parse(xml['xmlcontent'].strip())
        return {}
    
    
class SourceVia(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            #auth = NoAuth()
            #start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()
        start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')

        return [
            Orders(authenticator=auth, config=config, start_date=start_date)
        ]
    