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

class LiverpoolBase(HttpStream):

    url_base = "https://liverpool-prod.mirakl.net/api/"

    def __init__(
        self, 
        config: Mapping[str, Any],
        **kwargs
    ):
        super().__init__()
        self.api_key = config['api_key']
        self.shop_id = config['shop_id']
        self.merchant = config['merchant']
        self.start_offset = 0
        self.end_offset = 100
        self.end_of_records = False

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        headers = {
            "Authorization": self.api_key,
            "Accept": 'application/json',
            "Content-type": 'application/json'
        }

        return headers
    
    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        
        return f"{self.endpoint_name}?offset={self.start_offset}&max={self.end_offset}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        if self.end_of_records == True:
            return None

        self.start_offset += 100
        self.end_offset += 100

        return self.start_offset
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()

        if len(response_json[self.record_list_name]) == 0:
            self.end_of_records = True
            return []

        item_list = []

        for item in response_json[self.record_list_name]:
            item_json = {
                "data":item,
                "merchant": self.merchant.upper(),
                "source": "MX_LIVERPOOL",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": item[self.record_primary_key],
                "timeline": "historic",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False
            }

            item_list.append(item_json)
            
        return item_list

class Offers(LiverpoolBase):
    endpoint_name = 'offers'
    record_list_name = 'offers'
    record_key_name = 'offer'
    record_primary_key = 'product_sku'

    primary_key = None

class Orders(LiverpoolBase):

    cursor_field = "data_order"
    primary_key = "data_order"

    endpoint_name = 'orders'
    record_list_name = 'orders'
    record_key_name = 'order'
    record_primary_key = 'order_id'
    record_date_field = 'created_date'

    def __init__(
        self, 
        config: Mapping[str, Any], 
        start_date: datetime,
        **kwargs
    ):
        super().__init__(config)

        self.start_date = start_date

        self._cursor_value = None
    
    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ):
        
        start_date = self.start_date
        if self.cursor_field in stream_state.keys():
            start_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S') - timedelta(days=15)

        start_ingestion_date = datetime.strftime(start_date, '%Y-%m-%dT00:00:00Z')
        end_ingestion_date = datetime.strftime(datetime.now(), '%Y-%m-%dT23:59:59Z')

        params = {
            "start_date":start_ingestion_date,
            "end_date":end_ingestion_date,
            "shop_id":self.shop_id
        }

        return params 

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        
        latest_record_date = datetime.strptime(latest_record['data'][self.record_date_field], '%Y-%m-%dT%H:%M:%SZ')

        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}
    

class SourceLiverpool(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = NoAuth()
            start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')
            stream = Offers(authenticator=auth, config=config)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()
        start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')

        return [
            Offers(authenticator=auth, config=config),
            Orders(authenticator=auth, config=config, start_date=start_date)
        ]
