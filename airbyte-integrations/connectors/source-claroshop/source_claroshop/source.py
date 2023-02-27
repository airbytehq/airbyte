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
from airbyte_cdk.sources.streams import IncrementalMixin
from datetime import datetime, timedelta
from time import sleep
import base64
import hashlib
import json
import pytz
from threading import Thread
from threading import Lock
from source_claroshop.thread_safe_list import ThreadSafeList


class ClaroshopBase(HttpStream):
    '''
    Claroshop base class with default ingestion methods

    API Doc: PDF document

    Use the logger.info(str) function for debugging
    '''

    url_base = "https://selfservice.claroshop.com/apicm/v1/"

    def __init__(
        self, 
        config: Mapping[str, Any],
        **kwargs
    ):
        '''
        The following parameters must be present in all streams:
            endpoint_name: Claroshop API endpoint name   
            record_list_name: Return the name of the object list containing the data            
            record_key_name: The root key of a JSON object          
            record_primary_key: Data primary key
        '''
        super().__init__()
        self.api_keys = config['api_keys']
        self.merchant = config['merchant']
        self.page = 1
        self.end_of_pages = False

    def get_credentials_url(self,api_keys):
        keys = json.loads(base64.b64decode(api_keys))
        now = datetime.now(pytz.timezone('America/Mexico_City'))
        timestamp = now.strftime('%Y-%m-%dT%H:%M:%S')
        a_string = keys['public_key'] + timestamp + keys['private_key']
        signature = hashlib.sha256(a_string.encode('utf-8')).hexdigest()

        return keys['public_key'] + '/' + signature + '/' + timestamp
    
    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ):

        return None

    def log_percentage_progress(self, part, whole):
        logger.info(f'Progress: {round(100 * float(part)/float(whole), 2)}%')
    


class Productos(ClaroshopBase):

    #Always set primary_key to None for FULL ingestions
    primary_key = None

    endpoint_name = 'producto'
    record_list_name = 'productos'
    record_key_name = 'producto'
    record_primary_key = 'transactionid'

    def __init__(
        self,
        config,
        **kwargs
    ):
        super().__init__(config)
        self.read_products = 0


    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:

        transactionid = stream_slice['transactionid']

        logger.info('Producto ID: %s', transactionid)
        
        return f"{self.get_credentials_url(self.api_keys)}/{self.endpoint_name}/{transactionid}"  
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        return None
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()

        item_json = {
                "data":response_json[self.record_key_name],
                "merchant": self.merchant.upper(),
                "source": "MX_Claroshop",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": response_json[self.record_key_name][self.record_primary_key],
                "timeline": "historic",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False
        }

        self.read_products += 1
        self.log_percentage_progress(self.read_products, self.total_products)
            
        return [item_json]  

    def get_transactionid_list(self):
        path = self.url_base + self.initial_path()

        total_number_of_pages = requests.get(path).json()['totalpaginas']

        transactionid_list = []

        logger.info('GENERATING PRODUCT ID LIST')

        for i in range(1, total_number_of_pages+1):
            self.page = i

            path = self.url_base + self.initial_path()

            item_list = requests.get(path).json()['productos']

            [transactionid_list.append({'transactionid': item['transactionid']}) for item in item_list]
        
        logger.info('Products list: %s', transactionid_list)

        self.total_products = len(transactionid_list)

        return transactionid_list

    def initial_path(self):
        return f"{self.get_credentials_url(self.api_keys)}/{self.endpoint_name}?page={self.page}"  

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:

        return self.get_transactionid_list()
    
class Pedidos(ClaroshopBase):

    cursor_field = "data_pedido"
    primary_key = "data_pedido"

    endpoint_name = 'pedidosfiltros'
    record_key_name = 'pedido'
    record_primary_key = 'nopedido'
    record_date_field = 'fechaautorizacion'

    def __init__(
        self, 
        config: Mapping[str, Any], 
        start_date: datetime,
        **kwargs
    ):
        super().__init__(config)

        self.start_date = start_date

    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:

        logger.info(stream_slice)
        self.status_name = stream_slice['status_name']
        self.list_names = stream_slice['list_names']

        return f"{self.get_credentials_url(self.api_keys)}/{self.endpoint_name}?action={stream_slice['status_name']}&date_start={stream_slice['start_date']}&date_end={stream_slice['end_date']}"
    
    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ):

        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        return None
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()

        return_list = self.get_item_list(response_json, self.list_names[0])
    
        for list in self.list_names[1:]:
            return_list += self.get_item_list(response_json, list)
        
            
        return return_list
    
    def get_item_list(self, response_json, list_name):
        item_list = []

        for item in response_json['0'][list_name]:
            item_json = {
                "data":item,
                "merchant": self.merchant.upper(),
                "source": "MX_CLAROSHOP",
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

    
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        
        latest_record_date = datetime.strptime(latest_record['data'][self.record_date_field], '%Y-%m-%d')

        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT00:00:00')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}

    def _chunk_slices(self, start_date: datetime) -> List[Mapping[str, any]]:
        slices = []

        status_list = [
            {
                'status_name': 'entregados',
                'list_names': ['listaentregados']
            },
            {
                'status_name': 'pendientes',
                'list_names': ['listapendientes']
            },
            {
                'status_name': 'embarcados',
                'list_names': ['listaguiasautomaticas', 'listaguiasmanuales']
            }
        ]

        while start_date <= datetime.now():
            for status in status_list:
                slice = {}
                slice['status_name'] = status['status_name']
                slice['list_names'] = status['list_names']
                slice["start_date"] = datetime.strftime(start_date, "%Y-%m-%d")
                slice["end_date"] = datetime.strftime(start_date+timedelta(days=15), "%Y-%m-%d")
                slices.append(slice)
            
            start_date += timedelta(days=16)

        logger.info(slices)

        return slices

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:

        start_date = self.start_date

        if stream_state and self.cursor_field in stream_state:
            if isinstance(stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT00:00:00')
            else:
                current_stream_state_date = stream_state[self.cursor_field]

        start_date = current_stream_state_date - timedelta(days=15) if stream_state and self.cursor_field in stream_state else self.start_date
        return self._chunk_slices(start_date)

class PedidosDetalle(Pedidos):
    cursor_field = "data_pedido_detalle"
    primary_key = "data_pedido_detalle"

    endpoint_name = 'pedidosfiltros'
    record_key_name = 'pedido'
    record_primary_key = 'nopedido'
    record_date_field = 'fechacolocado'

    def __init__(
        self, 
        config: Mapping[str, Any], 
        start_date: datetime,
        **kwargs
    ):
        super().__init__(config, start_date)
        self.config = config
        self.start_date = start_date

    def pedido_detalle_path(
        self,
        nopedido
    ) -> str:

        return f"{self.url_base}/{self.get_credentials_url(self.api_keys)}/pedidos?action=detallepedido&nopedido={nopedido}"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()['0']

        item_list = []

        record_lists = [key for key in response_json.keys() if 'lista' in key]
        
        pedidos = []

        for record_list in record_lists:
            for record in response_json[record_list]:

                pedidos.append(record['nopedido'])

        item_list = ThreadSafeList()

        number_of_threds = 15

        threads = []

        for chunk in self.chunker_list(pedidos, number_of_threds):
            threads.append(Thread(target=self.read_pedido_detalle, args=(item_list, chunk)))

        # start threads
        for thread in threads:
            thread.start()
        
        # wait for all threads
        for thread in threads:
            thread.join()

        return item_list.get_list()
    
    def chunker_list(self, list, size):
        return (list[i::size] for i in range(size))
    
    def read_pedido_detalle(self, item_list, pedido_list):
        for nopedido in pedido_list:
            response_pedido = requests.get(self.pedido_detalle_path(nopedido))
            response_pedido_json = self.handle_json_error(response_pedido)

            while 'estatuspedido' not in response_pedido_json.keys():
                new_response = requests.get(self.pedido_detalle_path(nopedido))
                response_pedido_json = self.handle_json_error(new_response)

            logger.info('Pedido: %s', nopedido)

            item_json = {
                "data":response_pedido_json,
                "merchant": self.merchant.upper(),
                "source": "MX_CLAROSHOP",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": nopedido,
                "timeline": "historic",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False
            }

            item_list.append(item_json)

    def handle_json_error(self, response):
        read_json = False
        while read_json == False:
            try:
                json_return = response.json()
                read_json = True
            except:
                logger.info('Handling error')
                response = requests.get(response.url)
                pass

        return json_return

    
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        
        latest_record_date = datetime.strptime(latest_record['data']['estatuspedido'][self.record_date_field], '%Y-%m-%d %H:%M:%S')

        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:

        start_date = self.start_date

        if stream_state and self.cursor_field in stream_state:
            if isinstance(stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
            else:
                current_stream_state_date = stream_state[self.cursor_field]

        start_date = current_stream_state_date - timedelta(days=15) if stream_state and self.cursor_field in stream_state else self.start_date
        
        return super()._chunk_slices(start_date)


class SourceClaroshop(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # auth = NoAuth()
            # stream = Productos(authenticator=auth, config=config)
            # stream_slice = stream.stream_slices(sync_mode=SyncMode.full_refresh)[0]
            # records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
            # next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()  
        start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')

        return [
            Productos(authenticator=auth, config=config),
            Pedidos(authenticator=auth, config=config, start_date=start_date),
            PedidosDetalle(authenticator=auth, config=config, start_date=start_date)
        ]