#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import abc
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Dict

import requests
import json
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


class InfiniceptStream(HttpStream, abc.ABC):
    url_base = 'https://api.infinicept.com'

    @abc.abstractmethod
    def path_suffix(self):
        pass

    def __init__(self, config: Dict, response_parse_name: str, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.tenant_ids = config['tenantIdList']
        self.response_parse_name = response_parse_name

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for tenant_id in self.tenant_ids:
            yield { 'tenant_id': tenant_id }

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        tenant_id = stream_slice['tenant_id']
        return f"/api/{tenant_id}/{self.path_suffix()}"

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        headers = {
            'Accept': 'application/json',
            'x-AuthenticationKeyId': self.config['x-AuthenticationKeyId'],
            'x-AuthenticationKeyValue': self.config['x-AuthenticationKeyValue']
        }
        return headers

    def request_params(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            'PageSize': 1000
        }

        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        for record in response.json()[self.response_parse_name]:
            yield self.transform(record=record, tenant_id=stream_slice['tenant_id'])

    def transform(self, record: MutableMapping[str, Any], tenant_id: str)-> MutableMapping[str, Any]:
        record['tenant_id'] = tenant_id
        return record

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if decoded_response['totalPages'] > decoded_response['currentPage']:
            return { 'CurrentPage': decoded_response['currentPage'] + 1 }


class Transactions(InfiniceptStream):
    primary_key = 'id'

    def path_suffix(self):
        return 'transactions/paginated'


class FundingFailures(InfiniceptStream):
    primary_key = 'id'

    def path_suffix(self):
        return 'fundingreturns'


class Deposits(InfiniceptStream):
    primary_key = 'id'

    def path_suffix(self):
        return 'fundinginstructions/paged'


# Source
class SourceInfinicept(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        alive = True
        error_msg = None

        tenant_id = config['tenantIdList'][0]

        try:
            url = f'https://api.infinicept.com/api/{tenant_id}/fundinginstructions/paged?PageSize=1'
            headers = {
                'Accept': 'application/json',
                'x-AuthenticationKeyId': config['x-AuthenticationKeyId'],
                'x-AuthenticationKeyValue': config['x-AuthenticationKeyValue']
            }
            requests.request("GET", url, headers=headers)

        except json.decoder.JSONDecodeError as err:
            alive, error_msg = (
                False,
                f"Unable to connect to the Infinicept API with the provided credentials and Tenant Id {tenant_id}."
                " Please make sure the input credentials and tenant IDs are correct.",
            )

        return alive, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [
            Transactions(config=config, response_parse_name='transactions'),
            FundingFailures(config=config, response_parse_name='data'),
            Deposits(config=config, response_parse_name='data'),
        ]
