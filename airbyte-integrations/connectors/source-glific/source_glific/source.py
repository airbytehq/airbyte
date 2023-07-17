#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator

import requests
import json
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream



stream_json_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "id": {
            "type": [
                "number",
            ]
        }
    },
}

# Basic full refresh stream
class GlificStream(HttpStream, ABC):

    primary_key = None

    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class GlificStream(HttpStream, ABC)` which is the current class
    `class Customers(GlificStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(GlificStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalGlificStream((GlificStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    def __init__(self, stream_name: str, url_base: str, pagination_limit: int, credentials: dict, config: dict, **kwargs):
        super().__init__(**kwargs)

        self.stream_name = stream_name
        self.api_url = url_base
        self.credentials = credentials
        self.pagination_limit = pagination_limit
        self.start_time = config['start_time']
        self.offset = 0

    @property
    def url_base(self) -> str:
        return self.api_url
    
    @property
    def name(self) -> str:
        return self.stream_name
    
    @property
    def http_method(self) -> str:
        """All requests in the glific stream are posts with body"""
        return "POST"
    
    def get_json_schema(self) -> dict:
        """Return json schema of each stream"""
        return stream_json_schema
    
    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        json_resp = response.json()
        if json_resp['data']['organizationExportData'] is not None:
            records_str = json_resp['data']['organizationExportData']['data']
            records_obj = json.loads(records_str)
            if self.stream_name in records_obj['data']:
                records = json.loads(records_str)['data'][f'{self.stream_name}']
                # more records need to be fetched
                if len(records) == (self.pagination_limit + 1):
                    self.offset += 1
                    return {"offset": self.offset, "limit": self.pagination_limit}

        return None

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        """Add the authorization token in the headers"""
        return {'authorization': self.credentials['access_token'], 'Content-Type': 'application/json'}

    
    def request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Mapping:
        """Request body to post"""

        query = "query organizationExportData($filter: ExportFilter) { organizationExportData(filter: $filter) {data errors { key message } } }"
        
        filter_obj = {
            "startTime": self.start_time,
            "offset": self.offset,
            "limit": self.pagination_limit,
            "tables": [self.stream_name]
        }

        if next_page_token is not None:
            filter_obj["offset"] = next_page_token["offset"]
            filter_obj["limit"] = next_page_token["limit"]

        return {"query":  query, "variables": {"filter": filter_obj}}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        json_resp = response.json()
        if json_resp['data']['organizationExportData'] is not None:
            records_str = json_resp['data']['organizationExportData']['data']
            records_obj = json.loads(records_str)
            if self.stream_name in records_obj['data']:
                records = json.loads(records_str)['data'][f'{self.stream_name}']
                col_names = records[0].split(',')
                print("NOOO OFFF COOLLLSS", len(col_names))
                for i in range(1, len(records)): # each record
                    record = {}
                    print("RECORD NOO OOFFF VALLLSS",i, len(records[i].split(',')))
                    for j, col_val in enumerate(records[i].split(',')): # each col_val
                        record[col_names[j]] = col_val
                    yield record

# Source
class SourceGlific(AbstractSource):
    """Glific source"""

    API_URL = "https://api.staging.tides.coloredcow.com/api"
    PAGINATION_LIMIT = 500


    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        if 'phone' not in config:
            logger.info('Phone number missing')
            return False, "Phone number missing"

        if 'password' not in config:
            logger.info("Password missing")
            return False, "Password missing"

        endpoint = f"{self.API_URL}/v1/session"
        auth_payload = {
            "user": {
                "phone": config["phone"],
                "password": config["password"]
            }
        }

        response = requests.post(endpoint, json=auth_payload, timeout=30)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.info(err)
            return False, response.error.message

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        # authenticate and get the credentials for all streams
        endpoint = f"{self.API_URL}/v1/session"
        auth_payload = {
            "user": {
                "phone": config["phone"],
                "password": config["password"]
            }
        }
        try:
            response = requests.post(endpoint, json=auth_payload, timeout=30)
            response.raise_for_status()
            credentials = response.json()['data']
        except requests.exceptions.HTTPError:
            # return empty zero streams since authentication failed
            return []
        
        # fetch the export config for organization/client/user
        endpoint = f"{self.API_URL}"
        headers = {'authorization': credentials['access_token']}

        try:
            query = 'query organizationExportConfig { organizationExportConfig { data errors { key message } } }'
            variables = {}
            payload = {"query": query, "variables": variables}

            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.HTTPError:
            # return empty zero streams since config could not be fetched
            return []
        
        # construct streams
        export_config = json.loads(data['data']['organizationExportConfig']['data'])
        streams = []
        for table in export_config['tables']:
            stream_obj = GlificStream(table, self.API_URL, self.PAGINATION_LIMIT, credentials, config)
            streams.append(stream_obj)

        return streams
