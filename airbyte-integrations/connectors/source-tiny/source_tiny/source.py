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

class TinyBase(HttpStream):

    url_base = "https://api.tiny.com.br/api2/"

    def __init__(
        self, 
        config: Mapping[str, Any],
        **kwargs
    ):
        super().__init__()
        self.api_token = config['api_token']
        self.merchant = config['merchant']
        self.page = 1
        self.end_of_records = False
    
    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        
        return f"{self.endpoint_name}?token={self.api_token}&formato=json&pagina={self.page}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        if self.page == self.max_pages:
            return None

        self.page += 1

        return self.page
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()

        self.max_pages = int(response_json['retorno']['numero_paginas'])

        item_list = []

        for item in response_json['retorno'][self.record_list_name]:
            item_json = {
                "data":item[self.record_key_name],
                "merchant": self.merchant.upper(),
                "source": "BR_TINY",
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

    def chunker_list(self, list, size):
        return (list[i::size] for i in range(size))
    
    def handle_request_error(self, url):
        read_response = False
        while read_response == False:
            try:
                response = requests.get(url)
                read_response = True
            except:
                response = requests.get(url)
                pass

        return response
    
    def handle_json_error(self, url, json):

        while json['retorno']['status'] != 'OK':
            logger.info('Handling error')
            json = self.handle_request_error(url)
            logger.info(json['retorno'])
            sleep(30)

        return json


class NotasFiscais(TinyBase):
    endpoint_name = 'notas.fiscais.pesquisa.php'
    record_list_name = 'notas_fiscais'
    record_key_name = 'nota_fiscal'
    record_primary_key = 'numero'
    record_date_field = 'data_emissao'

    cursor_field = "data_nota_fiscal"
    primary_key = "data_nota_fiscal"

    def __init__(
        self, 
        config: Mapping[str, Any], 
        start_date: datetime,
        **kwargs
    ):
        super().__init__(config)

        self.start_date = start_date

        self._cursor_value = None

    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        
        start_date = self.start_date
        if self.cursor_field in stream_state.keys():
            start_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
        
        start_ingestion_date = datetime.strftime(start_date, '%d/%m/%Y')
        
        return f"{self.endpoint_name}?token={self.api_token}&formato=json&pagina={self.page}&dataInicial={start_ingestion_date}"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = self.handle_json_error(response.url, response.json())
        
        self.max_pages = int(response_json['retorno']['numero_paginas'])

        item_list = []

        for item in response_json['retorno'][self.record_list_name]:
            item_json = {
                "data":item[self.record_key_name],
                "merchant": self.merchant.upper(),
                "source": "BR_TINY",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": item[self.record_key_name][self.record_primary_key],
                "timeline": "historic",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False
            }
            
            item_json['data_xml'] = self.get_nf_xml(item_json)

            item_list.append(item_json)
        return item_list

    def get_nf_xml(self, item):
        nf_xml_path = "https://api.tiny.com.br/api2/nota.fiscal.obter.xml.php"

        xml = self.handle_request_error(f"{nf_xml_path}?id={item['data']['id']}&token={self.api_token}").content

        logger.info(item['data']['id'])
        
        try:
            xml_object = xmltodict.parse(xml.strip())

            while xml_object['retorno']['status'] != 'OK' and int(xml_object['retorno']['codigo_erro']) != 34:
                logger.info('Handling error XML')
                xml = self.handle_request_error(f"{nf_xml_path}?id={item['data']['id']}&token={self.api_token}").content
                xml_object = xmltodict.parse(xml.strip())

                logger.info(xml_object['retorno'])
                
                sleep(30)
        except:
            logger.info('Fatal for xml: %s', item['data']['id'])
            xml_object = {}
            pass

        sleep(1)
        
        try:
            return_object = {'xml_nfe': xml_object['retorno']['xml_nfe']}
            if 'xml_cancelamento' in xml_object['retorno'].keys():
                return_object['xml_cancelamento'] = xml_object['retorno']['xml_cancelamento']
        except Exception as e:
            logger.info('Error for xml: %s', item['data']['id'])
            return_object = xml_object
            logger.info(return_object)

            pass

        return return_object

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        
        latest_record_date = datetime.strptime(latest_record['data'][self.record_date_field], '%d/%m/%Y')

        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}
    

class SourceTiny(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = NoAuth()
            start_date = datetime.strptime(config['start_date'], '%d/%m/%Y') - timedelta(days=365)
            stream = NotasFiscais(authenticator=auth, config=config, start_date=start_date)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()
        start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')

        return [
            NotasFiscais(authenticator=auth, config=config, start_date=start_date)
        ]