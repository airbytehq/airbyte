from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import base64
import uuid
import json
import urllib.parse
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from datetime import datetime, timedelta, timezone
from airbyte_cdk.sources.streams.http.auth import NoAuth
# import pytz
from airbyte_cdk.models import SyncMode
# import xmltodict
# from time import sleep


class CoppelBase(HttpStream):
    url_base = "https://coppel.mirakl.net/api/"

    def __init__(
            self,
            config: Mapping[str, Any],
            **kwargs
    ):
        super().__init__()
        # self.api_key = config['api_key']
        self.Authorization = config['api_key']
        self.merchant = config['merchant']
        self.country = config['country']
        self.user_id = config['user_id']
        self.start_date = datetime.strptime(config['start_date'], '%Y-%m-%d') - timedelta(days=15)
        self.end_date = datetime.now().strftime("%Y-%m-%d")
        self.offset = 0

        self.limit = 100
        # self.end_of_records = False
        # self.count_n = 0

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        headers = {
            "Authorization": self.Authorization,
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

        if stream_state and (self.cursor_field in stream_state):
            if isinstance(stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%SZ')
            else:
                current_stream_state_date = stream_state[self.cursor_field]
            param_start_date = datetime.strftime(current_stream_state_date - timedelta(days=15), '%Y-%m-%d')
        else:
            param_start_date = datetime.strftime(self.start_date - timedelta(days=15), '%Y-%m-%d')

        params = {
            'start_date': param_start_date,
            'end_date': self.end_date,
            'max': self.limit,
            'offset': self.offset,
            'shop_id': self.user_id
        }
        concatenated = urllib.parse.urlencode(sorted(params.items()))

        return f"{self.endpoint_name}?{concatenated}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        logger.info('old_offset')
        logger.info(self.offset)
        if self.total_count == 0:
            self.offset = 0
            return None
        elif self.total_count - self.offset <= self.limit:
            self.offset = 0
            return None
        else:
            self.offset = self.offset + self.limit
        logger.info('new_offset')
        logger.info(self.offset)
        return self.offset


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()

        logger.info('total_count')
        logger.info(response_json['total_count'])
        self.total_count = response_json['total_count']

        item_list = []

        for item in response_json[self.record_list_name]:
            item_json = {
                "data": item,
                "merchant": self.merchant.upper(),
                "source": self.country.upper() + "_COPPEL",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": item[self.record_primary_key],
                "user_id": self.user_id,
                "timeline": "historic",
                "created_at": item[self.record_creation_date_key],
                "updated_at": item[self.record_update_date_key],
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": True
            }

            item_list.append(item_json)

        return item_list


class Orders(CoppelBase):

    cursor_field = 'created_date'
    endpoint_name = 'orders'
    record_list_name = 'orders'
    record_key_name = 'order'
    record_primary_key = 'order_id'
    record_creation_date_key = 'created_date'
    record_update_date_key = 'last_updated_date'
    # record_metadata_name = 'meta'

    primary_key = 'created_date'

    def __init__(
            self,
            config: Mapping[str, Any],
            start_date: datetime,
            **kwargs
    ):
        super().__init__(config)

        self.offset = 0
        self.total_count = 0
        self._cursor_value = None

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
                       ):

        return None

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        latest_record_date = datetime.strptime(latest_record['data'][self.record_creation_date_key], '%Y-%m-%dT%H:%M:%SZ')
        # logger.info('get_updated_state log:')
        # logger.info(latest_record_date)
        # logger.info(current_stream_state)
        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%SZ')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}


class Offers(CoppelBase):

    cursor_field = 'orderDate'
    endpoint_name = 'offers'
    record_list_name = 'offers'
    record_key_name = 'order'
    record_primary_key = 'offer_id'
    # record_creation_date_key = 'created_date'
    # record_update_date_key = 'last_updated_date'
    # record_metadata_name = 'meta'

    primary_key = 'created_date'

    def __init__(
            self,
            config: Mapping[str, Any],
            **kwargs
    ):
        super().__init__(config)

        self.offset = 0
        self.total_count = 0
        self._cursor_value = None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()

        logger.info('total_count')
        logger.info(response_json['total_count'])
        self.total_count = response_json['total_count']

        item_list = []
        timestamp_value = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

        for item in response_json[self.record_list_name]:
            item_json = {
                "data": item,
                "merchant": self.merchant.upper(),
                "source": self.country.upper() + "_COPPEL",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": item[self.record_primary_key],
                "user_id": self.user_id,
                "timeline": "snapshot",
                "created_at": timestamp_value,
                "updated_at": timestamp_value,
                "timestamp": timestamp_value,
                "sensible": True
            }

            item_list.append(item_json)

        return item_list

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
                       ):
        return None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        params = {
            'max': self.limit,
            'offset': self.offset,
            'shop_id': self.user_id
        }
        concatenated = urllib.parse.urlencode(sorted(params.items()))

        return f"{self.endpoint_name}?{concatenated}"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        return {}


class SourceCoppel(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # auth = NoAuth()
            # start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
            # stream = Orders(authenticator=auth, config=config, start_date=start_date)
            # stream = Items(authenticator=auth, config=config, start_date=start_date)
            # records = stream.read_records(sync_mode=SyncMode.full_refresh)
            # next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()
        start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')

        return [
            Orders(authenticator=auth, config=config, start_date=start_date)
            ,Offers(authenticator=auth, config=config)
        ]

# Durante a emissão da Credencial Plena, o titular poderá incluir dependentes, contudo, a Credencial Plena de dependentes maiores de 18 anos só estará disponível para uso
# após o dependente acessar o app Credencial Sesc ou site Central de Relacionamento Digital e realizar o aceite do termo de credenciamento.
