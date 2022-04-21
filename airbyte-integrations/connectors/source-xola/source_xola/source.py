import datetime
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Dict

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from urllib.parse import urlparse
from urllib.parse import parse_qs


# Basic full refresh stream
class XolaStream(HttpStream, ABC):
    url_base = "https://xola.com/api/"
    x_api_key = None

    def __init__(self, x_api_key: str, **kwargs):
        self.x_api_key = x_api_key
        super().__init__(kwargs)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..
        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        paging_info = None

        if "paging" in response.json().keys():
            next_url = response.json()["paging"]["next"]
            parsed_url = urlparse(next_url)
            paging_info = {}
            if 'skip' in parse_qs(parsed_url.query).keys():
                skip = parse_qs(parsed_url.query)['skip'][0]
                paging_info['skip'] = skip
            if 'sort' in parse_qs(parsed_url.query).keys():
                sort = parse_qs(parsed_url.query)['sort'][0]
                paging_info['sort'] = sort
            if 'id[lt]' in parse_qs(parsed_url.query).keys():
                lt_id_key = parse_qs(parsed_url.query)['id[lt]'][0]
                paging_info['id[lt]'] = lt_id_key
            if 'limit' in parse_qs(parsed_url.query).keys():
                limit = parse_qs(parsed_url.query)['limit'][0]
                paging_info['limit'] = limit

        return paging_info

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        return [response.json()]

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        headers: Dict[str, str] = {
            "Accept": "application/json",
            "X-API-VERSION": "2017-06-10",
            "X-API-KEY": self.x_api_key,
            "sort": "-id"
        }
        return headers


class Orders(XolaStream):
    primary_key = "order_id"
    cursor_field = "updatedAt"
    seller_id = None

    def __init__(self, seller_id: str, x_api_key: str, cursor_field: str, **kwargs):
        super().__init__(x_api_key, **kwargs)
        self.seller_id = seller_id
        if cursor_field:
            self.cursor_field = cursor_field

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        should return "orders". Required.
        """
        print("stream state ", stream_state)
        path = "orders"
        if stream_state is not None and self.cursor_field in stream_state:
            path = path + "?" + self.cursor_field + "=" + stream_state[self.cursor_field]
        print("path ", path)
            
        return path

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        seller id is returned as a form of parameters
        """
        params = {}
        if next_page_token:
            for key in next_page_token.keys():
                params[key] = next_page_token[key]
        params['seller'] = self.seller_id
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        raw_response = response.json()["data"]
        modified_response = []
        for data in raw_response:
            try:
                # Tags._id
                resp = {"tags": []}
                for tag in data["tags"]:
                    resp["tags"].append({"id": tag["id"]})

                resp["order_id"] = data["id"]

                if "createdAt" in data.keys(): resp["createdAt"] = data["createdAt"]
                if "customerName" in data.keys(): resp["customerName"] = data["customerName"]
                if "customerEmail" in data.keys(): resp["customerEmail"] = data["customerEmail"]
                if "travelers" in data.keys(): resp["travelers"] = data["travelers"]
                if "source" in data.keys(): resp["source"] = data["source"]
                if "createdBy" in data.keys(): resp["createdBy"] = data["createdBy"]
                if "quantity" in data.keys(): resp["quantity"] = data["quantity"]
                if "event" in data.keys(): resp["event"] = data["event"]
                if "amount" in data.keys(): resp["amount"] = data["amount"]
                if "updatedAt" in data.keys(): resp["updatedAt"] = data["updatedAt"]
                if "type" in data.keys(): resp["type"] = data["type"]
                modified_response.append(resp)
            except:
                pass
        return modified_response

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
            Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        latest_record_date = latest_record[self.cursor_field]
        print("orders stream ", current_stream_state)
        if current_stream_state is not None and self.cursor_field in current_stream_state.keys():
            current_parsed_date = current_stream_state[self.cursor_field]

            print("current parsed date ", current_stream_state)
            print("latest record ", latest_record)
           
            
            if current_parsed_date is not None:
                return {self.cursor_field: max(current_parsed_date, latest_record_date)}
            else:
                return {self.cursor_field: latest_record_date}
        else:
            return {self.cursor_field: latest_record_date}

class Transactions(XolaStream):
    primary_key = "id"
    seller_id = None
    cursor_field = "updatedAt"

    def __init__(self, seller_id: str, x_api_key: str, cursor_field: str, **kwargs):
        super().__init__(x_api_key, **kwargs)
        self.seller_id = seller_id
        self.cursor_field = cursor_field

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        should return "orders". Required.
        """
        path = "transactions"
        if stream_state is not None and self.cursor_field in stream_state:
            path += "?" + self.cursor_field + "=" + stream_state[self.cursor_field]
        return path
    

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        seller id is returned as a form of parameters
        """
        params = {}
        if next_page_token:
            for key in next_page_token.keys():
                params[key] = next_page_token[key]
        params['seller'] = self.seller_id
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        raw_response = response.json()["data"]
        modified_response = []
        for data in raw_response:

            resp = {"id": data["id"]}

            if "amount" in data.keys(): resp["amount"] = data["amount"]
            if "balance" in data.keys(): resp["balance"] = data["balance"]
            if "createdAt" in data.keys(): resp["createdAt"] = data["createdAt"]
            if "currency" in data.keys(): resp["currency"] = data["currency"]
            if "method" in data.keys(): resp["method"] = data["method"]
            if "source" in data.keys(): resp["source"] = data["source"]
            if "type" in data.keys(): resp["type"] = data["type"]

            if "order" in data.keys():
                if isinstance(data["order"], dict):
                    resp["order_id"] = data["order"]["id"]
                else:
                    resp["order_id"] = data["order"]
            else:
                resp["order_id"] = ""

            if "seller" in data.keys():
                if isinstance(data["seller"], dict):
                    resp["seller_id"] = data["seller"]["id"]
                else:
                    resp["seller_id"] = data["seller"]
            else:
                resp["seller_id"] = ""

            if "createdBy" in data.keys():
                if isinstance(data["createdBy"], dict):
                    resp["createdBy"] = data["createdBy"]["id"]
                else:
                    resp["createdBy"] = data["createdBy"]
            else:
                resp["createdBy"] = ""

            modified_response.append(resp)
        return modified_response

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
           Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        latest_record_date = latest_record[self.cursor_field]
        print("transactions stream ", current_stream_state)
        if current_stream_state is not None and self.cursor_field in current_stream_state.keys():
            current_parsed_date = current_stream_state[self.cursor_field]

            print("current parsed date ", current_stream_state)
            print("latest record ", latest_record)
           
            
            if current_parsed_date is not None:
                return {self.cursor_field: max(current_parsed_date, latest_record_date)}
            else:
                return {self.cursor_field: latest_record_date}
        else:
            return {self.cursor_field: latest_record_date}


# Basic incremental stream


class IncrementalXolaStream(XolaStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails
    #  for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.
        :return str: The name of the cursor field.
        """
        return ["updatedAt"]

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
            Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        latest_record_date = latest_record[self.cursor_field]
        print("common stream ", current_stream_state)
        if current_stream_state is not None and self.cursor_field in current_stream_state.keys():
            current_parsed_date = current_stream_state[self.cursor_field]

            print("current parsed date ", current_stream_state)
            print("latest record ", latest_record)
           
            
            if current_parsed_date is not None:
                return {self.cursor_field: max(current_parsed_date, latest_record_date)}
            else:
                return {self.cursor_field: latest_record_date}
        else:
            return {self.cursor_field: latest_record_date}

# Source
class SourceXola(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        x_api_key = config["x-api-key"]
        seller_id = config["seller-id"]
        url = "https://xola.com/api/orders"

        headers = {
            "Accept": "application/json",
            "X-API-VERSION": "2017-06-10",
            "X-API-KEY": x_api_key,
        }

        params = {
            "seller": seller_id
        }

        response = requests.request("GET", url, params=params, headers=headers)
        if response.status_code == 200:
            return True, None
        if response.status_code == 404:
            return False, f'seller id: {seller_id} NOT FOUND'
        return False, f'status code returned {response.status_code}. UNAUTHORISED'

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        cursor_field = 'updatedAt'
        
        if "cursor_field" in config.keys():
            cursor_field = config['cursor_field']
            
        return [
            Orders(x_api_key=config['x-api-key'],
                   seller_id=config['seller-id'],
                   cursor_field=cursor_field),
            Transactions(x_api_key=config['x-api-key'], seller_id=config['seller-id'],cursor_field=cursor_field)
        ]
