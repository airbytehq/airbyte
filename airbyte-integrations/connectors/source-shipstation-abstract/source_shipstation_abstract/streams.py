
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from airbyte_cdk.sources.streams.core import SyncMode
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from requests.auth import AuthBase
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
import datetime
import time


class ShipstationAbstractStream(HttpStream, ABC):
    url_base = "https://ssapi.shipstation.com/"
    primary_key = "id"
    limit = 50
    data_field = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        json_response = response.json()
        if "page" in json_response and "pages" in json_response:
            current_page = json_response["page"]
            total_pages = json_response["pages"]
            if current_page < total_pages:
                return {"page": current_page + 1}
        return None
    
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {}
        if next_page_token:
            params["page"] = next_page_token.get("page")
        return params

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.data_field, []) if self.data_field is not None else json_response

        if records is not None:
            for record in records:
                yield record
        else:
            err_msg = (
                f"Response contained no valid JSON data. Response body: {response.text}\n"
                f"Response status: {response.status_code}\n"
                f"Response body: {response.text}\n"
                f"Response headers: {response.headers}\n"
                f"Request URL: {response.request.url}\n"
                f"Request body: {response.request.body}\n"
            )
            # do NOT print request headers as it contains auth token
            self.logger.info(err_msg)


# class ShipstationStreamMetadataPagination(ShipstationAbstractStream):
#     def request_params(
#         self,
#         stream_state: Mapping[str, Any],
#         stream_slice: Mapping[str, Any] = None,
#         next_page_token: Mapping[str, Any] = None,
#     ) -> MutableMapping[str, Any]:
#         params = {}
#         if not next_page_token:
#             params = {"page_size": self.limit}
#         return params

#     def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
#         next_page_url = response.json()["_metadata"].get("next", False)
#         if next_page_url:
#             return {"next_page_url": next_page_url.replace(self.url_base, "")}

#     @staticmethod
#     @abstractmethod
#     def initial_path() -> str:
#         """
#         :return: initial path for the API endpoint if no next metadata url found
#         """

#     def path(
#         self,
#         stream_state: Mapping[str, Any] = None,
#         stream_slice: Mapping[str, Any] = None,
#         next_page_token: Mapping[str, Any] = None,
#     ) -> str:
#         if next_page_token:
#             return next_page_token["next_page_url"]
#         return self.initial_path()
    


class Users(ShipstationAbstractStream):
    def path(self, **kwargs) -> str:
        return self.url_base + "users"
    
class Carriers(ShipstationAbstractStream):
    def path(self, **kwargs) -> str:
        return self.url_base + "carriers"

class Stores(ShipstationAbstractStream):
    def path(self, **kwargs) -> str:
        return self.url_base + f"stores"
    
class MarketPlaces(ShipstationAbstractStream):
    def path(self, **kwargs) -> str:
        return self.url_base + "stores/marketplaces"
    
class Warehouses(ShipstationAbstractStream):
    def path(self, **kwargs) -> str:
        return self.url_base + "warehouses"
    
    
# incremental stream
class IncrementalShipstationAbstractStream(ShipstationAbstractStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = 1
        self.current_page = 1

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.page > self.current_page:
            self.current_page += 1
            return {"page": 1}
        return None
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        pass
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        pass


MAX_PAGE_SIZE = 10

class Shipments(IncrementalShipstationAbstractStream):
    primary_key = None

    @property
    def http_method(self) -> str:
        return "GET"

    def path(self, **kwargs) -> str:
        return self.url_base + "shipments"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if "shipments" in response_json:
            total = response_json['total']
            if total is not None and total > (MAX_PAGE_SIZE * self.current_page):
                self.page += 1
            results = response_json["shipments"]
            if results is None:
                return []
            return results
        else:
            raise Exception([{"message": "Failed to obtain data.", "msg": response.text}])
        
class Fulfillments(IncrementalShipstationAbstractStream):
    primary_key = None

    @property
    def http_method(self) -> str:
        return "GET"

    def path(self, **kwargs) -> str:
        return self.url_base + "fulfillments"


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if "fulfillments" in response_json:
            total = response_json['total']
            if total is not None and total > (MAX_PAGE_SIZE * self.current_page):
                self.page += 1
            results = response_json["fulfillments"]
            if results is None:
                return []
            return results
        else:
            raise Exception([{"message": "Failed to obtain data.", "msg": response.text}])
        
class Customers(IncrementalShipstationAbstractStream):
    primary_key = None

    @property
    def http_method(self) -> str:
        return "GET"

    def path(self, **kwargs) -> str:
        return self.url_base + "customers"


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if "customers" in response_json:
            total = response_json['total']
            if total is not None and total > (MAX_PAGE_SIZE * self.current_page):
                self.page += 1
            results = response_json["customers"]
            if results is None:
                return []
            return results
        else:
            raise Exception([{"message": "Failed to obtain data.", "msg": response.text}])
        
class Products(IncrementalShipstationAbstractStream):
    primary_key = None

    @property
    def http_method(self) -> str:
        return "GET"

    def path(self, **kwargs) -> str:
        return self.url_base + "products"


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if "products" in response_json:
            total = response_json['total']
            if total is not None and total > (MAX_PAGE_SIZE * self.current_page):
                self.page += 1
            results = response_json["products"]
            if results is None:
                return []
            return results
        else:
            raise Exception([{"message": "Failed to obtain data.", "msg": response.text}])
        


class Orders(IncrementalShipstationAbstractStream):
    primary_key = None

    @property
    def http_method(self) -> str:
        return "GET"

    def path(self, **kwargs) -> str:
        return self.url_base + "orders"


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if "orders" in response_json:
            total = response_json['total']
            if total is not None and total > (MAX_PAGE_SIZE * self.current_page):
                self.page += 1
            results = response_json["orders"]
            if results is None:
                return []
            return results
        else:
            raise Exception([{"message": "Failed to obtain data.", "msg": response.text}])
        
        
        
class GetStore(ShipstationAbstractStream):
    def __init__(self, authenticator, config):
        super().__init__(authenticator=authenticator)
        self.config = config
        # self.authenticator = authenticator

    def path(self, **kwargs) -> str:
        return self.url_base + "stores/" + kwargs.get("stores_id")
    

    def read_records(self, sync_mode, **kwargs):
        api_key = self.config["api_key"]
        api_secret = self.config["api_secret"]
        payload = {}
        stores_id = self.config.get("stores_id", None)
        if stores_id is None:
            raise Exception("Missing stores_id in kwargs.")
        
        url = self.path(stores_id=stores_id)
        response = requests.get(url, auth=(api_key, api_secret), params=payload)
        
        if response.status_code == 200:
            data = []
            store_data = response.json()
            data.append(store_data)
            for record in data:
                emitted_at = int(time.mktime(datetime.datetime.now().timetuple()))
                yield AirbyteRecordMessage(stream="get_store", data=record, emitted_at=emitted_at)
        else:
            raise Exception("Failed to retrieve get_store data.")



    
