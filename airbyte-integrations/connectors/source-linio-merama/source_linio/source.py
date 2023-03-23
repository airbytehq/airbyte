# from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Iterator

import requests
# from airbyte_cdk.models import (
#     AirbyteMessage,
#     ConfiguredAirbyteStream,
#     SyncMode,
# )
# from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
# from airbyte_cdk.models import Type as MessageType
# from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
import urllib.parse
from hashlib import sha256
from hmac import HMAC
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from datetime import datetime, timedelta, timezone
from airbyte_cdk.sources.streams.http.auth import NoAuth
import pytz
# import logging
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
    timezone_options = {
        'MX': pytz.timezone('America/Mexico_City'),
        'CL': pytz.timezone('America/Santiago'),
        'CO': pytz.timezone('America/Bogota'),
        'PE': pytz.timezone('America/Lima')
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
                try:
                    current_stream_state_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%d %H:%M:%S')
                except:
                    current_stream_state_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
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
            'Timestamp': datetime.now(self.timezone_options[self.country]).isoformat(),
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
        self.orders_list = []

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
                       ):

        return None

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        try:
            latest_record_date = datetime.strptime(latest_record['data'][self.record_creation_date_key], '%Y-%m-%d %H:%M:%S')
        except:
            latest_record_date = datetime.strptime(latest_record['data'][self.record_creation_date_key], '%Y-%m-%dT%H:%M:%S')
        logger.info('get_updated_state log:')
        logger.info(latest_record_date)
        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                try:
                    current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%d %H:%M:%S')
                except:
                    current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}
            # return {self.cursor_field: max(latest_record_date, current_stream_state_date), 'orders_list': self.orders_list}

        return {self.cursor_field: latest_record_date}
        # return {self.cursor_field: latest_record_date, 'orders_list': self.orders_list}

    def path_order_items(
            self,
            order_id: str
    ) -> str:

        params = {
            'Action': 'GetOrderItems',
            'UserID': self.user_id,
            'Version': '1.0',
            'Format': 'JSON',
            'Timestamp': datetime.now(self.timezone_options[self.country]).isoformat(),
            'OrderId': order_id
        }
        concatenated = urllib.parse.urlencode(sorted(params.items()))
        self.Signature = HMAC(self.api_key.encode(), concatenated.encode('utf-8'), sha256).hexdigest()

        # logger.info(f"?{concatenated}&Signature={self.Signature}")
        return f"?{concatenated}&Signature={self.Signature}"

    def parse_response_order_items(self, response: requests.Response) -> Iterable[Mapping]:

        order_items_record_list_name_1 = 'SuccessResponse'
        order_items_record_list_name_2 = 'Body'
        order_items_record_list_name_3 = 'OrderItems'
        order_items_record_list_name_4 = 'OrderItem'
        order_items_record_key_name = 'order_items'
        order_items_record_primary_key = 'OrderItemId'
        order_items_record_creation_date_key = 'CreatedAt'
        order_items_record_update_date_key = 'UpdatedAt'
        # order_items_record_metadata_name = 'Head'
        response_json = response.json()[order_items_record_list_name_1]

        item_list = []

        if isinstance(response_json[order_items_record_list_name_2][order_items_record_list_name_3][order_items_record_list_name_4], list):

            for item in response_json[order_items_record_list_name_2][order_items_record_list_name_3][order_items_record_list_name_4]:
                item_json = {
                    "order_items_data": item,
                    "merchant": self.merchant.upper(),
                    "source": self.country + "_LINIO",
                    "type": f"{self.merchant.lower()}_{order_items_record_key_name}",
                    "id": item[order_items_record_primary_key],
                    "user_id": self.user_id,
                    "timeline": "historic",
                    "created_at": item[order_items_record_creation_date_key],
                    "updated_at": item[order_items_record_update_date_key],
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "sensible": True
                }
                item_list.append(item_json)

        elif isinstance(response_json[order_items_record_list_name_2][order_items_record_list_name_3][order_items_record_list_name_4], dict):
            item = response_json[order_items_record_list_name_2][order_items_record_list_name_3][order_items_record_list_name_4]
            item_json = {
                "order_items_data": item,
                "merchant": self.merchant.upper(),
                "source": self.country + "_LINIO",
                "type": f"{self.merchant.lower()}_{order_items_record_key_name}",
                "id": item[order_items_record_primary_key],
                "user_id": self.user_id,
                "timeline": "historic",
                "created_at": item[order_items_record_creation_date_key],
                "updated_at": item[order_items_record_update_date_key],
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": True
            }
            item_list.append(item_json)

        else:
            pass
        return item_list

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
                order_id_items_request = self.url_base + self.path_order_items(item[self.record_primary_key])
                items_json_data = self.parse_response_order_items(response=requests.request('GET', order_id_items_request, headers={"Content-Type":"application/json"}))
                item.update({'items_data_request': items_json_data})
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

                # if item[self.record_primary_key] not in self.orders_list:
                #     self.orders_list.append(item[self.record_primary_key])
                item_list.append(item_json)

        return item_list


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

        if isinstance(response_json[self.record_list_name_2][self.record_list_name_3], dict):
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
        logger.info('Products TotalCount')
        logger.info(self.totalCount)

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
            'Timestamp': datetime.now(self.timezone_options[self.country]).isoformat()
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


# class order_items(LinioBase):
#
#     # cursor_field = 'CreatedAt'
#     endpoint_name = 'GetOrderItems'
#     record_list_name_1 = 'SuccessResponse'
#     record_list_name_2 = 'Body'
#     record_list_name_3 = 'OrderItems'
#     record_list_name_4 = 'OrderItem'
#     record_key_name = 'order_items'
#     record_primary_key = 'OrderItemId'
#     record_creation_date_key = 'CreatedAt'
#     record_update_date_key = 'UpdatedAt'
#     record_metadata_name = 'Head'
#
#     primary_key = 'OrderItemId'
#
#     def __init__(
#             self,
#             config: Mapping[str, Any],
#             **kwargs
#     ):
#         super().__init__(config)
#
#         # self.CreatedAfter = datetime.strptime(config['CreatedAfter'], '%Y-%m-%d')
#         # self.offset = 0
#         # self.totalCount = 0
#         self._cursor_value = None
#
#     def path(
#             self,
#             stream_state: Mapping[str, Any] = None,
#             stream_slice: Mapping[str, Any] = None,
#             next_page_token: Mapping[str, Any] = None
#     ) -> str:
#
#         params = {
#             'Action': self.endpoint_name,
#             'UserID': self.user_id,
#             'Version': '1.0',
#             'Format': 'JSON',
#             'Timestamp': datetime.now(self.timezone_options[self.country]).isoformat(),
#             'OrderId': stream_slice['OrderId']
#         }
#         concatenated = urllib.parse.urlencode(sorted(params.items()))
#         self.Signature = HMAC(self.api_key.encode(), concatenated.encode('utf-8'), sha256).hexdigest()
#
#         logger.info(f"?{concatenated}&Signature={self.Signature}")
#         return f"?{concatenated}&Signature={self.Signature}"
#
#     def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
#                        ):
#         return None
#
#     def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
#
#         return None
#
#     def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
#
#         response_json = response.json()[self.record_list_name_1]
#
#         item_list = []
#
#         if isinstance(response_json[self.record_list_name_2][self.record_list_name_3][self.record_list_name_4], list):
#
#             for item in response_json[self.record_list_name_2][self.record_list_name_3][self.record_list_name_4]:
#                 item_json = {
#                     "data": item,
#                     "merchant": self.merchant.upper(),
#                     "source": self.country + "_LINIO",
#                     "type": f"{self.merchant.lower()}_{self.record_key_name}",
#                     "id": item[self.record_primary_key],
#                     "user_id": self.user_id,
#                     "timeline": "historic",
#                     "created_at": item[self.record_creation_date_key],
#                     "updated_at": item[self.record_update_date_key],
#                     "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
#                     "sensible": True
#                 }
#                 item_list.append(item_json)
#
#         elif isinstance(response_json[self.record_list_name_2][self.record_list_name_3][self.record_list_name_4], dict):
#             item = response_json[self.record_list_name_2][self.record_list_name_3][self.record_list_name_4]
#             item_json = {
#                 "data": item,
#                 "merchant": self.merchant.upper(),
#                 "source": self.country + "_LINIO",
#                 "type": f"{self.merchant.lower()}_{self.record_key_name}",
#                 "id": item[self.record_primary_key],
#                 "user_id": self.user_id,
#                 "timeline": "historic",
#                 "created_at": item[self.record_creation_date_key],
#                 "updated_at": item[self.record_update_date_key],
#                 "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
#                 "sensible": True
#             }
#             item_list.append(item_json)
#
#         else:
#             pass
#         return item_list
#     def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
#
#         return {}
#
#     def _chunk_slices(self, list_of_orders: list) -> List[Mapping[str, any]]:
#         slices = []
#
#         for order_id in list_of_orders:
#             slice = {}
#             slice['order_id'] = order_id
#             slices.append(slice)
#
#         logger.info('slices content log:')
#         logger.info(slices)
#
#         return slices
#
#     def stream_slices(
#             self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None,
#             state_manager=None
#     ) -> Iterable[Optional[Mapping[str, any]]]:
#
#         # orders_state = state.get('orders', {}).get('stream_state', None)
#         # state_manager.get_stream_state(stream_name, stream_instance.namespace)
#         logger.info('testing state_manager value')
#         # logger.info(ConnectorStateManager)
#         # state_manager = ConnectorStateManager(stream_instance_map=stream_instances, state=state)
#         order_items_list = ConnectorStateManager.get_stream_state(stream_name='orders', namespace='orders')
#         logger.info(order_items_list)
#         logger.info(self.force_error)
#         # logger.info(stream_name.get())
#         list_of_orders = ["8302912", "8306146"]
#
#         return self._chunk_slices(list_of_orders)



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

    # def _read_incremental(
    #     self,
    #     logger: logging.Logger,
    #     stream_instance: Stream,
    #     configured_stream: ConfiguredAirbyteStream,
    #     state_manager: ConnectorStateManager,
    #     internal_config: InternalConfig,
    # ) -> Iterator[AirbyteMessage]:
    #     """Read stream using incremental algorithm
    #
    #     :param logger:
    #     :param stream_instance:
    #     :param configured_stream:
    #     :param state_manager:
    #     :param internal_config:
    #     :return:
    #     """
    #     stream_name = configured_stream.stream.name
    #     stream_state = state_manager.get_stream_state(stream_name, stream_instance.namespace)
    #
    #     if stream_state and "state" in dir(stream_instance):
    #         stream_instance.state = stream_state
    #         logger.info(f"Setting state of {stream_name} stream to {stream_state}")
    #
    #     slices = stream_instance.stream_slices(
    #         cursor_field=configured_stream.cursor_field,
    #         sync_mode=SyncMode.incremental,
    #         stream_state=stream_state,
    #         state_manager=state_manager
    #     )
    #     logger.debug(f"Processing stream slices for {stream_name} (sync_mode: incremental)", extra={"stream_slices": slices})
    #
    #     total_records_counter = 0
    #     has_slices = False
    #     for _slice in slices:
    #         has_slices = True
    #         logger.debug("Processing stream slice", extra={"slice": _slice})
    #         records = stream_instance.read_records(
    #             sync_mode=SyncMode.incremental,
    #             stream_slice=_slice,
    #             stream_state=stream_state,
    #             cursor_field=configured_stream.cursor_field or None,
    #         )
    #         record_counter = 0
    #         for message_counter, record_data_or_message in enumerate(records, start=1):
    #             message = self._get_message(record_data_or_message, stream_instance)
    #             yield message
    #             if message.type == MessageType.RECORD:
    #                 record = message.record
    #                 stream_state = stream_instance.get_updated_state(stream_state, record.data)
    #                 checkpoint_interval = stream_instance.state_checkpoint_interval
    #                 record_counter += 1
    #                 if checkpoint_interval and record_counter % checkpoint_interval == 0:
    #                     yield self._checkpoint_state(stream_instance, stream_state, state_manager)
    #
    #                 total_records_counter += 1
    #                 # This functionality should ideally live outside of this method
    #                 # but since state is managed inside this method, we keep track
    #                 # of it here.
    #                 if self._limit_reached(internal_config, total_records_counter):
    #                     # Break from slice loop to save state and exit from _read_incremental function.
    #                     break
    #
    #         yield self._checkpoint_state(stream_instance, stream_state, state_manager)
    #         if self._limit_reached(internal_config, total_records_counter):
    #             return
    #
    #     if not has_slices:
    #         # Safety net to ensure we always emit at least one state message even if there are no slices
    #         checkpoint = self._checkpoint_state(stream_instance, stream_state, state_manager)
    #         yield checkpoint

# Durante a emissão da Credencial Plena, o titular poderá incluir dependentes, contudo, a Credencial Plena de dependentes maiores de 18 anos só estará disponível para uso
# após o dependente acessar o app Credencial Sesc ou site Central de Relacionamento Digital e realizar o aceite do termo de credenciamento.
