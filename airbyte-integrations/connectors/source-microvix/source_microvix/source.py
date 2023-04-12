#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import json
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from datetime import datetime, timedelta
from airbyte_cdk.sources.streams.http.auth import NoAuth
from airbyte_cdk.models import SyncMode
from time import sleep

class MicrovixBase(HttpStream):

    url_base = "https://webapi.microvix.com.br/1.0/api/integracao"

    def __init__(
        self, 
        config: Mapping[str, Any],
        **kwargs
    ):
        super().__init__()
        self.user = config['user']
        self.password = config['password']
        self.chave = config['chave']
        self.cnpj = config['cnpj']
        self.merchant = config['merchant']

        
    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        
        return None 

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        return None
    
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = eval(json.loads(json.dumps(response.content.decode("utf-8"))))

        item_list = []

        for item in response_json[self.record_list_name]:
            item_json = {
                "data":item,
                "merchant": self.merchant.upper(),
                "source": "BR_MICROVIX",
                "type": f"{self.merchant.lower()}_notafiscal",
                "id": item[self.record_primary_key],
                "timeline": "historic",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": False
            }

            item_list.append(item_json)

        return item_list
    
    @property
    def http_method(self) -> str:
        """
        Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.
        """
        return "POST"

class XmlDocumentos(MicrovixBase):
    record_list_name = 'ResponseData'
    record_primary_key = 'chave_nfe'

    cursor_field = "data_nota_fiscal"
    primary_key = "data_nota_fiscal"

    record_date_field = "data_emissao"


    def __init__(
        self, 
        config: Mapping[str, Any], 
        start_date: datetime,
        **kwargs
    ):
        super().__init__(config)

        self.start_date = start_date

        self._cursor_value = None

    def request_body_data(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):

        body= f"""
        <?xml version="1.0" encoding="utf-8" ?>
        <LinxMicrovix>
            <Authentication user="{self.user}" password="{self.password}" />
            <ResponseFormat>json</ResponseFormat>
            <Command>
                <Name>LinxXMLDocumentos</Name>
                <Parameters>
                    <Parameter id="chave">{self.chave}/</Parameter>
                    <Parameter id="cnpjEmp">{self.cnpj}</Parameter>
                    <Parameter id="data_inicial">{stream_slice['start_ingestion_date']}</Parameter>
                    <Parameter id="data_fim">{stream_slice['end_ingestion_date']}</Parameter>
                    <Parameter id="timestamp">0</Parameter>
                </Parameters>
            </Command>
        </LinxMicrovix>
        """
        logger.info(stream_slice)

        return body.strip()
    
    def generate_date_list(self, start_date):
        end_date = datetime.now()

        start_ingestion_date = start_date
        end_ingestion_date = start_date + timedelta(days=14)

        date_list = []

        date_list.append({
                'start_ingestion_date': datetime.strftime(start_ingestion_date, '%Y-%m-%d'),
                'end_ingestion_date': datetime.strftime(end_ingestion_date, '%Y-%m-%d')
            })


        while end_ingestion_date < end_date:
            start_ingestion_date = end_ingestion_date + timedelta(days=1)
            end_ingestion_date = start_ingestion_date + timedelta(days=14)

            date_list.append({
                'start_ingestion_date': datetime.strftime(start_ingestion_date, '%Y-%m-%d'),
                'end_ingestion_date': datetime.strftime(end_ingestion_date, '%Y-%m-%d')
            })

        return date_list
    
    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:

        start_date = self.start_date

        if stream_state and self.cursor_field in stream_state:
            if isinstance(stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT00:00:00')
            else:
                current_stream_state_date = stream_state[self.cursor_field]

        start_date = current_stream_state_date if stream_state and self.cursor_field in stream_state else self.start_date

        logger.info(start_date)
        return self.generate_date_list(start_date)
    
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        
        latest_record_date = datetime.strptime(latest_record['data'][self.record_date_field], '%d/%m/%Y 00:00:00')

        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT00:00:00')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}
    

class SourceMicrovix(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # auth = NoAuth()
            # start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')
            # stream = Offers(authenticator=auth, config=config)
            # records = stream.read_records(sync_mode=SyncMode.full_refresh)
            # next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()
        start_date = datetime.strptime(config['start_date'], '%d/%m/%Y')

        return [
            XmlDocumentos(authenticator=auth, config=config, start_date = start_date)
        ]
    

