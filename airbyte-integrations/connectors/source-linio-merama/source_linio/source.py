# from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import uuid
# import json
import urllib.parse
from hashlib import sha256
from hmac import HMAC
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from datetime import datetime, timedelta, timezone
from airbyte_cdk.sources.streams.http.auth import NoAuth
# from airbyte_cdk.models import SyncMode
# import xmltodict
# from time import sleep


class LinioBase(HttpStream):
    url_base = 'https://sellercenter-api.linio.com.mx'
    url_country_base = {'MX': 'https://sellercenter-api.linio.com.mx',
                        'CL': 'https://sellercenter-api.linio.cl',
                        'CO': 'https://sellercenter-api.linio.com.co',
                        'PE': 'https://sellercenter-api.linio.com.pe'
                        }
    def __init__(
            self,
            config: Mapping[str, Any],
            **kwargs
    ):
        super().__init__()
        self.country = config['country'].upper()
        self.url_base = self.url_country_base[self.country]
        self.api_key = config['api_keys']
        self.Signature = None
        self.merchant = config['merchant']
        self.user_id = config['user_id']

        self.CreatedAfter = datetime.strptime(config['CreatedAfter'], '%Y-%m-%d')

        self.limit = 1000
        self.offset = 0

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        headers = {
            "Content-type": 'application/json',
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
                current_stream_state_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%d %H:%M:%S')
            else:
                current_stream_state_date = stream_state[self.cursor_field]
            param_CreatedAfter = datetime.strftime(current_stream_state_date - timedelta(days=15), '%Y-%m-%d')
        else:
            param_CreatedAfter = datetime.strftime(self.CreatedAfter - timedelta(days=15), '%Y-%m-%d')

        params = {
            'Action': self.endpoint_name,
            'UserID': self.user_id,
            'Version': '1.0',
            'Format': 'JSON',
            'Limit': self.limit,
            'Timestamp': datetime.now().isoformat(),
            'CreatedAfter': param_CreatedAfter,
            'Offset': self.offset
        }
        concatenated = urllib.parse.urlencode(sorted(params.items()))
        self.Signature = HMAC(self.api_key.encode(), concatenated.encode('utf-8'), sha256).hexdigest()

        logger.info(f"?{concatenated}&Signature={self.Signature}")
        return f"?{concatenated}&Signature={self.Signature}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        logger.info('old_offset')
        logger.info(self.offset)
        if self.totalCount == 0:
            self.offset = 0
            return None
        elif self.totalCount - self.offset <= self.limit:
            self.offset = 0
            return None
        else:
            self.offset = self.offset + self.limit
        logger.info('new_offset')
        logger.info(self.offset)
        return self.offset

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()[self.record_list_name_1]
        # logger.info(response_json['Head'])
        logger.info('TotalCount')
        logger.info(response_json[self.record_metadata_name]['TotalCount'])
        self.totalCount = int(response_json[self.record_metadata_name]['TotalCount'])

        item_list = []
        self.new_initial_date = self.CreatedAfter

        if self.totalCount > 0:

            for item in response_json[self.record_list_name_2][self.record_list_name_3][self.record_list_name_4]:
                item_json = {
                    "data": item,
                    "merchant": self.merchant.upper(),
                    "source": self.country + "_LINIO",
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


class Orders(LinioBase):

    cursor_field = 'CreatedAt'
    endpoint_name = 'GetOrders'
    record_list_name_1 = 'SuccessResponse'
    record_list_name_2 = 'Body'
    record_list_name_3 = 'Orders'
    record_list_name_4 = 'Order'
    record_key_name = 'order'
    record_primary_key = 'OrderId'
    record_creation_date_key = 'CreatedAt'
    record_update_date_key = 'UpdatedAt'
    record_metadata_name = 'Head'

    primary_key = 'OrderId'

    def __init__(
            self,
            config: Mapping[str, Any],
            **kwargs
    ):
        super().__init__(config)

        self.CreatedAfter = datetime.strptime(config['CreatedAfter'], '%Y-%m-%d')
        self.offset = 0
        self.totalCount = 0
        self._cursor_value = None

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
                       ):

        return None

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        latest_record_date = datetime.strptime(latest_record['data'][self.record_creation_date_key], '%Y-%m-%d %H:%M:%S')
        logger.info('get_updated_state log:')
        logger.info(latest_record_date)
        logger.info(current_stream_state)
        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%d %H:%M:%S')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}


class Products(LinioBase):

    # cursor_field = 'CreatedAt'
    endpoint_name = 'GetProducts'
    record_list_name_1 = 'SuccessResponse'
    record_list_name_2 = 'Body'
    record_list_name_3 = 'Products'
    record_list_name_4 = 'Product'
    record_key_name = 'product'
    record_primary_key = 'ProductId'
    record_creation_date_key = 'SaleStartDate'
    record_update_date_key = 'SaleEndDate'
    record_metadata_name = 'Head'

    primary_key = 'ProductId'

    def __init__(
            self,
            config: Mapping[str, Any],
            **kwargs
    ):
        super().__init__(config)

        self.CreatedAfter = datetime.strptime(config['CreatedAfter'], '%Y-%m-%d')
        self.offset = 0
        self.totalCount = 0
        self._cursor_value = None

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
                       ):
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()[self.record_list_name_1]


        item_list = []
        self.new_initial_date = self.CreatedAfter

        if self.record_list_name_4 in response_json[self.record_list_name_2][self.record_list_name_3].keys():
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

            for item in response_json[self.record_list_name_2][self.record_list_name_3][self.record_list_name_4]:
                item_json = {
                    "data": item,
                    "merchant": self.merchant.upper(),
                    "source": self.country + "_LINIO",
                    "type": f"{self.merchant.lower()}_{self.record_key_name}",
                    "id": item[self.record_primary_key],
                    "user_id": self.user_id,
                    "timeline": "historic",
                    "created_at": item[self.record_creation_date_key],
                    "updated_at": timestamp,
                    "timestamp": timestamp,
                    "sensible": True
                }
                item_list.append(item_json)

        self.totalCount = self.totalCount + len(item_list)

        return item_list

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        return {}


class Statistics(LinioBase):

    # cursor_field = 'CreatedAt'
    endpoint_name = 'GetStatistics'
    record_list_name_1 = 'SuccessResponse'
    record_list_name_2 = 'Body'
    record_key_name = 'statistics'
    # record_primary_key = 'ProductId'
    record_creation_date_key = 'Timestamp'
    record_metadata_name = 'Head'

    primary_key = 'id'

    def __init__(
            self,
            config: Mapping[str, Any],
            **kwargs
    ):
        super().__init__(config)

        self.CreatedAfter = datetime.strptime(config['CreatedAfter'], '%Y-%m-%d')
        self.offset = 0
        self.totalCount = 0
        self._cursor_value = None

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
                       ):
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        return None

    def path(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:

        params = {
            'Action': self.endpoint_name,
            'UserID': self.user_id,
            'Version': '1.0',
            'Format': 'JSON',
            'Timestamp': datetime.now().isoformat()
        }
        concatenated = urllib.parse.urlencode(sorted(params.items()))
        self.Signature = HMAC(self.api_key.encode(), concatenated.encode('utf-8'), sha256).hexdigest()

        logger.info(f"?{concatenated}&Signature={self.Signature}")
        return f"?{concatenated}&Signature={self.Signature}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()[self.record_list_name_1]

        item_list = []

        try:
            timestamp_created_date = datetime.strptime(response_json[self.record_metadata_name][self.record_creation_date_key], '%Y-%m-%dT%H:%M:%S%z').astimezone(tz=timezone.utc).replace(tzinfo=None)
        except:
            timestamp_created_date = datetime.strptime(response_json[self.record_metadata_name][self.record_creation_date_key], '%Y-%m-%dT%H:%M:%S.%f')

        item_json = {
            "data": response_json[self.record_list_name_2],
            "merchant": self.merchant.upper(),
            "source": self.country + "_LINIO",
            "type": f"{self.merchant.lower()}_{self.record_key_name}",
            "id": self.merchant.lower() + '_' + self.user_id + '_' + timestamp_created_date.strftime("%Y-%m-%d"),
            "user_id": self.user_id,
            "timeline": "snapshot",
            "created_at": timestamp_created_date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "updated_at": timestamp_created_date.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "sensible": True
        }
        item_list.append(item_json)

        return item_list

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        return {}



class SourceLinio(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # auth = NoAuth()
            # CreatedAfter = datetime.strptime(config['CreatedAfter'], '%Y-%m-%d')
            # stream = Orders(authenticator=auth, config=config, CreatedAfter=CreatedAfter)
            # stream = Items(authenticator=auth, config=config, CreatedAfter=CreatedAfter)
            # records = stream.read_records(sync_mode=SyncMode.full_refresh)
            # next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()

        return [
            Orders(authenticator=auth, config=config),
            Products(authenticator=auth, config=config),
            Statistics(authenticator=auth, config=config)
        ]

# Durante a emissão da Credencial Plena, o titular poderá incluir dependentes, contudo, a Credencial Plena de dependentes maiores de 18 anos só estará disponível para uso
# após o dependente acessar o app Credencial Sesc ou site Central de Relacionamento Digital e realizar o aceite do termo de credenciamento.
