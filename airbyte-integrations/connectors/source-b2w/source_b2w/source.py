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
import xmltodict

class B2WBase(HttpStream):

    url_base = "https://api.skyhub.com.br/fulfillment/b2w/"

    def __init__(
        self, 
        config: Mapping[str, Any],
        **kwargs
    ):
        super().__init__()
        self.X_User_Email = config['X_User_Email']
        self.x_Api_Key = config['x_Api_Key']
        self.x_accountmanager_key = config['x_accountmanager_key']
        self.merchant = config['merchant']
        self.page = 0
        self.end_of_records = False


    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        headers = {
            "X-User-Email": self.X_User_Email,
            "x-Api-Key": self.x_Api_Key,
            "x-accountmanager-key": self.x_accountmanager_key
        }

        self.headers = headers

        return headers
    
    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        
        path = f"{self.endpoint_name}?from_date={self.start_date.strftime('%d/%m/%Y')}&to_date={datetime.now().strftime('%d/%m/%Y')}&page={self.page}"
        
        return path
    
    def xml_path(self, xml_nfes_path):

        if xml_nfes_path == None: 
            return {}

        xml_path = self.url_base + xml_nfes_path.split('/b2w')[1]

        response = requests.get(xml_path, headers=self.headers)

        if 'nfes' in response.json().keys():

            for nfe in response.json()['nfes']:

                xml_json = xmltodict.parse(nfe['xml_content'].strip())

                if 'AG - Ret Simb Merc em AG' not in xml_json['nfeProc']['NFe']['infNFe']['ide']['natOp']:
                    return xml_json   
                         
        return {}   

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        if self.end_of_records == True:
            return None

        self.page += 1

        return self.page
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()

        if response.status_code == 404:
            self.end_of_records = True
            return []
        elif response.status_code != 200:
            raise

        item_list = []

        for item in response_json[self.record_list_name]:
            
            item_json = {
                "data":item,
                "data_xml": self.xml_path(item['xml_nfes_path']),
                "merchant": self.merchant.upper(),
                "source": "BR_B2W",
                "type": f"{self.merchant.lower()}_order",
                "id": item[self.record_primary_key],
                "timeline": "historic",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False
            }

            item_list.append(item_json)

        sleep(5)    
            
        return item_list

class Delivery(B2WBase):

    cursor_field = "data_nota_fiscal"
    primary_key = "data_nota_fiscal"

    endpoint_name = 'delivery'
    record_list_name = 'deliveries'
    # record_key_name = 'order'
    record_primary_key = 'order_access_key'
    record_date_field = 'invoice_sent_at'

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Override if needed. If set to False, allows opting-out of raising HTTP code exception.
        """
        return False

    def __init__(
        self, 
        config: Mapping[str, Any], 
        start_date: datetime,
        **kwargs
    ):
        super().__init__(config)

        self.start_date = start_date

        self._cursor_value = None

    
    
    # def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    # ):
        
    #     start_date = self.start_date
    #     if self.cursor_field in stream_state.keys():
    #         start_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S') - timedelta(days=15)

    #     start_ingestion_date = datetime.strftime(start_date, '%Y-%m-%dT00:00:00Z')
    #     end_ingestion_date = datetime.strftime(datetime.now(), '%Y-%m-%dT23:59:59Z')

    #     params = {
    #         "start_date":start_ingestion_date,
    #         "end_date":end_ingestion_date,
    #         "shop_id":self.shop_id
    #     }

    #     return params 

    # def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
   
    #     latest_record_date = datetime.strptime(latest_record['data'][self.record_date_field], '%Y-%m-%dT%H:%M:%SZ')

    #     if current_stream_state.get(self.cursor_field):
    #         if isinstance(current_stream_state[self.cursor_field], str):
    #             current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
    #         else:
    #             current_stream_state_date = current_stream_state[self.cursor_field]

    #         return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

    #     return {self.cursor_field: latest_record_date}
    
        

class SourceB2W(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # auth = NoAuth()
            # start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')
            # stream = Deliveries(authenticator=auth, config=config)
            # records = stream.read_records(sync_mode=SyncMode.full_refresh)
            # next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()
        start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')

        return [
            Delivery(authenticator=auth, config=config, start_date=start_date)
        ]
    
    
