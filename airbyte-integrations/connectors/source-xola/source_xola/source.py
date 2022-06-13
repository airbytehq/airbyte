import datetime
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Dict

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from urllib.parse import urlparse
from urllib.parse import parse_qs
from datetime import datetime
import time
import logging
import traceback

LOGGER = logging.getLogger()

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

# incremental stream
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
        return "updatedAt"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
            Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        latest_record_date = latest_record[self.cursor_field]
        if current_stream_state is not None and self.cursor_field in current_stream_state.keys():
            current_parsed_date = current_stream_state[self.cursor_field]
            
            if current_parsed_date is not None:
                return {self.cursor_field: max(current_parsed_date, latest_record_date)}
            else:
                return {self.cursor_field: latest_record_date}
        else:
            return {self.cursor_field: latest_record_date}
        
        
    def read_records(
        self, sync_mode: SyncMode, stream_state: Mapping[str, Any] = None, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        slice = super().read_records(sync_mode=sync_mode, stream_slice=stream_slice, stream_state=stream_state)
        yield from self.filter_records_newer_than_state(stream_state=stream_state, records_slice=slice)

    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Mapping[str, Any] = None) -> Iterable:
        if stream_state:
            for record in records_slice:
                if record[self.cursor_field] > stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice

    
class Orders(IncrementalXolaStream):
    primary_key = "order_id"
    cursor_field = "updatedAt"
    seller_id = None

    def __init__(self, seller_id: str, x_api_key: str, **kwargs):
        super().__init__(x_api_key, **kwargs)
        self.seller_id = seller_id

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        should return "orders". Required.
        """
        return "orders"

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
        
        if self.cursor_field in stream_state.keys():
            params[self.cursor_field + '[gt]'] = stream_state[self.cursor_field]
            
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

class Users(IncrementalXolaStream):
    primary_key = "id"
    cursor_field = "order_updatedAt"
    seller_id = None

    def __init__(self, seller_id: str, x_api_key: str, **kwargs):
        super().__init__(x_api_key, **kwargs)
        self.seller_id = seller_id

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        should return "users". Required.
        """
        return "orders"

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
        
        if self.cursor_field in stream_state.keys():
            params[self.cursor_field + '[gt]'] = stream_state[self.cursor_field]
            
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
                organiserAdded = False
                
                user_resp = {}
                
                user_resp["order_id"] = data["id"]
                user_resp["waiver_createdAt"] = data["createdAt"]
                user_resp["waiver_updatedAt"] = data["updatedAt"]
                user_resp["order_createdAt"] = data["createdAt"]
                user_resp["order_updatedAt"] = data["updatedAt"]
                
                if "customerName" in data.keys(): user_resp["customerName"] = data["customerName"]
                if "customerEmail" in data.keys(): user_resp["customerEmail"] = data["customerEmail"]
                if "phone" in data.keys(): user_resp["phone"] = data["phone"]
                if "dateOfBirth" in data.keys(): user_resp["dateOfBirth"] = data["dateOfBirth"]
                
                user_resp["user_id"] = data["traveler"]["id"] if "traveler" in data.keys() and isinstance(data["traveler"], dict) else ""
                
                ## Fetch waivers information.
                if "waivers" in data.keys():
                    for waiver in data["waivers"]:
                        if "participants" in waiver.keys():   
                            for participant in waiver["participants"]:
                                resp = {}

                                resp["order_id"] = data["id"]
                                try:
                                    if isinstance(waiver["createdAt"], dict):
                                        resp["waiver_createdAt"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(waiver["createdAt"]["sec"])) + "+00:00"
                                    else:
                                        resp["waiver_createdAt"] = waiver["createdAt"]
                                    
                                    if isinstance(waiver["updatedAt"], dict):
                                        resp["waiver_updatedAt"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(waiver["updatedAt"]["sec"])) + "+00:00"
                                    else:
                                        resp["waiver_updatedAt"] = waiver["updatedAt"] 
                                except Exception as e:
                                    traceback.print_exc()
                                    LOGGER.info("Error occurred while parsing waiver createdAt and updatedAt", e)
                                
                                resp["order_updatedAt"] = data["updatedAt"]
                                resp["order_createdAt"] = data["createdAt"]

                                if "customerName" in participant.keys(): resp["customerName"] = participant["customerName"]
                                if "customerEmail" in participant.keys() and participant["customerEmail"]: resp["customerEmail"] = participant["customerEmail"]
                                if "phone" in participant.keys(): resp["phone"] = participant["phone"]
                                if "dateOfBirth" in participant.keys(): resp["dateOfBirth"] = participant["dateOfBirth"]
                                
                                resp["user_id"] = participant["traveler"]["$id"]["$id"] if "traveler" in participant.keys() and "$id" in participant["traveler"].keys() else ""

                                if (resp["customerEmail"], resp["customerName"]) == (user_resp["customerEmail"], user_resp["customerName"]):
                                    if organiserAdded == False:
                                        organiserAdded = True
                                        if resp["user_id"].empty(): resp["user_id"] = user_resp["user_id"]
                                        modified_response.append(resp)
                                else:
                                    modified_response.append(resp)
                                    
                if organiserAdded == False:
                    modified_response.append(user_resp)
            except:
                pass
        return modified_response
    
class Transactions(IncrementalXolaStream):
    primary_key = "id"
    seller_id = None
    cursor_field = "updatedAt"

    def __init__(self, seller_id: str, x_api_key: str, **kwargs):
        super().__init__(x_api_key, **kwargs)
        self.seller_id = seller_id

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        should return "transactions". Required.
        """
        return "transactions"

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
                
        if self.cursor_field in stream_state.keys():
            params[self.cursor_field + '[gt]'] = stream_state[self.cursor_field]
        
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
            if "updatedAt" in data.keys(): resp["updatedAt"] = data["updatedAt"]
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
        
        return [
            Orders(x_api_key=config['x-api-key'], seller_id=config['seller-id']),
            Transactions(x_api_key=config['x-api-key'], seller_id=config['seller-id']),
            Users(x_api_key=config['x-api-key'], seller_id=config['seller-id'])
        ]
