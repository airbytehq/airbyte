from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import base64
import uuid
import json
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from datetime import datetime, timedelta, timezone
from airbyte_cdk.sources.streams.http.auth import NoAuth
from airbyte_cdk.models import SyncMode
# import xmltodict
# from time import sleep


class WalmartMarketplaceBase(HttpStream):
    url_base = "https://marketplace.walmartapis.com/v3/"

    def __init__(
            self,
            config: Mapping[str, Any],
            **kwargs
    ):
        super().__init__()
        self.client_id = json.loads(base64.b64decode(config['api_keys']).decode('utf-8'))['client_id']
        self.client_secret = json.loads(base64.b64decode(config['api_keys']).decode('utf-8'))['client_secret']
        self.access_token = None
        self.Authorization = 'Basic ' + base64.b64encode((self.client_id + ':' + self.client_secret).encode('utf-8')).decode('utf-8')
        self.WM_MARKET = config['WM_MARKET']
        self.merchant = config['merchant']
        self.user_id = config['user_id']
        self.createdStartDate = datetime.strptime(config['createdStartDate'], '%Y-%m-%d') - timedelta(days=15)
        self.createdEndDate = datetime.now().strftime("%Y-%m-%d")

        self.limit = 100
        self.timedelta_to_sum = 0
        self.end_of_records = False
        self.count_n = 0

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        self.count_n += 1
        logger.info(self.count_n)
        headers = {
            "Authorization": self.Authorization,
            "Accept": 'application/json',
            "Content-type": 'application/x-www-form-urlencoded',
            "WM_SVC_VERSION": '1.0.0',
            "WM_SVC.NAME": 'Merama Walmart Service',
            "WM_QOS.CORRELATION_ID": uuid.uuid4().hex,
            "WM_MARKET": self.WM_MARKET
        }

        if self.access_token == None or self.count_n > 300:
            response = requests.request('POST', 'https://marketplace.walmartapis.com/v3/token', headers=headers, params={"grant_type": 'client_credentials'})
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                headers.update({"WM_SEC.ACCESS_TOKEN": self.access_token})
                headers["WM_QOS.CORRELATION_ID"] = uuid.uuid4().hex
            else:
                logger.error('ERROR! Cannot get access token, verify the config data')
                return None
        else:
            headers.update({"WM_SEC.ACCESS_TOKEN": self.access_token})

        return headers

    def path(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:

        return f"{self.endpoint_name}?limit={self.limit}&createdStartDate={self.createdStartDate}&createdEndDate={self.createdEndDate}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        # if self.end_of_records == True:
        #     return None
        #
        # self.createdStartDate = self.new_initial_date + timedelta(days=self.timedelta_to_sum)
        # if self.createdStartDate > datetime.strptime(self.createdEndDate, "%Y-%m-%d"):
        #     self.createdEndDate = self.createdStartDate
        #
        # return self.createdStartDate

        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        response_json = response.json()
        # logger.info(response_json)
        logger.info('totalCount')
        logger.info(response_json[self.record_metadata_name]['totalCount'])
        logger.info('limit')
        logger.info(response_json[self.record_metadata_name]['limit'])
        self.totalCount = response_json[self.record_metadata_name]['totalCount']
        # if response_json[self.record_metadata_name]['totalCount'] < response_json[self.record_metadata_name]['limit']:
        #     self.timedelta_to_sum = 1
        # if response_json[self.record_metadata_name]['totalCount'] == 0:
        #     self.end_of_records = True
        #     return []

        item_list = []
        self.new_initial_date = self.createdStartDate

        for item in response_json[self.record_list_name]:
            item_json = {
                "data": item,
                "merchant": self.merchant.upper(),
                "source": self.WM_MARKET + "_WALMART",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": item[self.record_primary_key],
                "user_id": self.user_id,
                "timeline": "historic",
                "created_at": item[self.record_creation_date_key],
                "updated_at": item[self.record_update_date_key_1][0][self.record_update_date_key_2][0][self.record_update_date_key_3],
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "sensible": True
            }

            item_list.append(item_json)
        if len(response_json[self.record_list_name]) > 0:
            self.new_initial_date = datetime.strptime(response_json[self.record_list_name][0][self.record_creation_date_key], '%Y-%m-%dT%H:%M:%S.%f%z')

        return item_list


class Orders(WalmartMarketplaceBase):

    cursor_field = 'orderDate'
    endpoint_name = 'orders'
    record_list_name = 'order'
    record_key_name = 'order'
    record_primary_key = 'purchaseOrderId'
    record_creation_date_key = 'orderDate'
    record_update_date_key_1 = 'orderLines'
    record_update_date_key_2 = 'orderLineStatus'
    record_update_date_key_3 = 'statusDate'
    record_metadata_name = 'meta'

    primary_key = 'orderDate'

    def __init__(
            self,
            config: Mapping[str, Any],
            createdStartDate: datetime,
            **kwargs
    ):
        super().__init__(config)

        self.createdStartDate = datetime.strptime(config['createdStartDate'], '%Y-%m-%d')
        self.offset = 0
        self.totalCount = 0
        self._cursor_value = None

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
                       ):

        # createdStartDate = self.createdStartDate
        # logger.info('stream_state content')
        # logger.info(stream_state)
        # if self.cursor_field in stream_state.keys():
        #     if isinstance(stream_state[self.cursor_field], str):
        #         createdStartDate = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S') - timedelta(days=15)
        #     else:
        #         createdStartDate = stream_state[self.cursor_field] - timedelta(days=15)
        #     # createdStartDate = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S') - timedelta(days=15)
        #
        # start_ingestion_date = datetime.strftime(createdStartDate + timedelta(days=self.timedelta_to_sum), '%Y-%m-%dT00:00:00Z')
        # end_ingestion_date = datetime.strftime(datetime.now(), '%Y-%m-%dT23:59:59Z')
        #
        # params = {
        #     "createdStartDate": start_ingestion_date,
        #     "createdEndDate": end_ingestion_date,
        #     "limit": 100
        # }
        # logger.info(params)
        #
        # return params
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        # self.next_page_token = xmltodict.parse(response.text)['ns2:ItemResponses'][self.next_page_token_key]
        logger.info('old_offset')
        logger.info(self.offset)
        if self.totalCount == 0:
            self.offset = 0
            return None
        elif self.totalCount - self.offset  <= self.limit:
            self.offset = 0
            return None
        else:
            self.offset = self.offset + self.limit
            if self.offset > 1000:
                logger.info('offset must bigger than one thousand for this day!')
                self.offset = 0
                return None
        logger.info('new_offset')
        logger.info(self.offset)
        return self.offset
        # return None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:

        # logger.info(stream_slice)
        param_createdStartDate = stream_slice['createdStartDate']
        param_createdEndDate = stream_slice['createdEndDate']
        param_limit = stream_slice['limit']
        # param_createdStartDate = self.createdStartDate
        # param_createdEndDate = self.createdEndDate
        # param_limit = self.limit
        param_offset = self.offset

        return f"{self.endpoint_name}?limit={param_limit}&createdStartDate={param_createdStartDate}&createdEndDate={param_createdEndDate}&offset={param_offset}"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        latest_record_date = datetime.strptime(latest_record['data'][self.record_creation_date_key], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(tz=timezone.utc).replace(tzinfo=None)
        # logger.info('get_updated_state log:')
        # logger.info(latest_record_date)
        # logger.info(current_stream_state)
        if current_stream_state.get(self.cursor_field):
            if isinstance(current_stream_state[self.cursor_field], str):
                try:
                    current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
                except:
                    current_stream_state_date = datetime.strptime(current_stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(tz=timezone.utc).replace(tzinfo=None)
            else:
                current_stream_state_date = current_stream_state[self.cursor_field]

            return {self.cursor_field: max(latest_record_date, current_stream_state_date)}

        return {self.cursor_field: latest_record_date}

    def _chunk_slices(self, createdStartDate: datetime) -> List[Mapping[str, any]]:
        slices = []

        while createdStartDate <= datetime.now():
            # for status in status_list:
            slice = {}
            slice['limit'] = 100
            slice["createdStartDate"] = datetime.strftime(createdStartDate, "%Y-%m-%dT00:00:00Z")
            slice["createdEndDate"] = datetime.strftime(createdStartDate, "%Y-%m-%dT23:59:59Z")
            slice['offset'] = 0
            slices.append(slice)

            createdStartDate += timedelta(days=1)

        logger.info('slices content log:')
        logger.info(slices)

        return slices

    def stream_slices(
            self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:

        # createdStartDate = self.createdStartDate

        if stream_state and (self.cursor_field in stream_state):
            if isinstance(stream_state[self.cursor_field], str):
                try:
                    current_stream_state_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S')
                except:
                    current_stream_state_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(tz=timezone.utc).replace(tzinfo=None)
            else:
                current_stream_state_date = stream_state[self.cursor_field]

        createdStartDate = current_stream_state_date - timedelta(
            days=15) if stream_state and self.cursor_field in stream_state else self.createdStartDate

        return self._chunk_slices(createdStartDate)


class Items(WalmartMarketplaceBase):

    endpoint_name = 'items'
    record_list_name = 'ItemResponse'
    record_key_name = 'item'
    record_primary_key = 'wpid'
    next_page_token_key = 'nextCursor'

    primary_key = 'id'

    def __init__(
            self,
            config: Mapping[str, Any],
            **kwargs
    ):
        super().__init__(config)

        self.next_page_token_value = '*'
        self.limit = '50'

        self._cursor_value = None

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        self.count_n += 1
        logger.info(self.count_n)
        headers = {
            "Authorization": self.Authorization,
            "Accept": 'application/json',
            "Content-type": 'application/x-www-form-urlencoded',
            "WM_SVC_VERSION": '1.0.0',
            "WM_SVC.NAME": 'Merama Walmart Service',
            "WM_QOS.CORRELATION_ID": uuid.uuid4().hex,
            "WM_MARKET": self.WM_MARKET
        }

        if self.access_token == None or self.count_n > 300:
            response = requests.request('POST', 'https://marketplace.walmartapis.com/v3/token', headers=headers, params={"grant_type": 'client_credentials'})
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                headers.update({"WM_SEC.ACCESS_TOKEN": self.access_token})
                headers["WM_QOS.CORRELATION_ID"] = uuid.uuid4().hex
            else:
                logger.error('ERROR! Cannot get access token, verify the config data')
                return None
        else:
            headers.update({"WM_SEC.ACCESS_TOKEN": self.access_token})

        headers["Accept"] = 'application/xml'
        headers["Content-type"] = 'application/json'

        return headers

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
                       ):
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        logger.info(response.json().keys())
        if self.next_page_token_key in response.json().keys():
            self.next_page_token_value = response.json()[self.next_page_token_key]
        else:
            return None

        return self.next_page_token_value

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:

        param_nextCursor = self.next_page_token_value
        param_limit = self.limit

        return f"{self.endpoint_name}?limit={param_limit}&nextCursor={param_nextCursor}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        logger.info(response.text)
        # response_dict = xmltodict.parse(response.text)['ns2:ItemResponses']
        response_dict = response.json()
        # logger.info(response_json)

        item_list = []
        self.new_initial_date = self.createdStartDate
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

        for item in response_dict[self.record_list_name]:
            item_json = {
                "data": item,
                "merchant": self.merchant.upper(),
                "source": self.WM_MARKET + "_WALMART",
                "type": f"{self.merchant.lower()}_{self.record_key_name}",
                "id": item[self.record_primary_key],
                "user_id": self.user_id,
                "timeline": "historic",
                "created_at": timestamp,
                "updated_at": timestamp,
                "timestamp": timestamp,
                "sensible": False
            }

            item_list.append(item_json)

        return item_list

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        return {}



class SourceWalmartMarketplace(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            # auth = NoAuth()
            # createdStartDate = datetime.strptime(config['createdStartDate'], '%Y-%m-%d')
            # stream = Orders(authenticator=auth, config=config, createdStartDate=createdStartDate)
            # stream = Items(authenticator=auth, config=config, createdStartDate=createdStartDate)
            # records = stream.read_records(sync_mode=SyncMode.full_refresh)
            # next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = NoAuth()
        createdStartDate = datetime.strptime(config['createdStartDate'], '%Y-%m-%d')

        return [
            Orders(authenticator=auth, config=config, createdStartDate=createdStartDate)
            ,Items(authenticator=auth, config=config)
        ]

# Durante a emissão da Credencial Plena, o titular poderá incluir dependentes, contudo, a Credencial Plena de dependentes maiores de 18 anos só estará disponível para uso
# após o dependente acessar o app Credencial Sesc ou site Central de Relacionamento Digital e realizar o aceite do termo de credenciamento.
