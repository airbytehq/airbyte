
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from airbyte_cdk.sources.streams.core import SyncMode
import requests
from airbyte_cdk.sources.streams.http import HttpStream


class ShipstationAbstractStream(HttpStream, ABC):
    url_base = "https://ssapi.shipstation.com/"
    primary_key = "userId"
    limit = 50
    data_field = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

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
        return self.url_base + "stores"
    
class MarketPlaces(ShipstationAbstractStream):
    def path(self, **kwargs) -> str:
        return self.url_base + "stores/marketplaces"
    
    
# class Fulfillments(ShipstationAbstractStream):
#     def path(self, **kwargs) -> str:
#         return self.url_base + "fulfillments"
    
#     def read_records(self, sync_mode: SyncMode, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
#         response = self._send_request("GET", self.path())
#         json_response = response.json()
#         fulfillments = json_response.get("fulfillments", [])
        
#         if not fulfillments:
#             # No fulfillments available, return an empty list
#             return []
        
#         # Process the fulfillments and yield them as records
#         for fulfillment in fulfillments:
#             # Process fulfillment and yield it as a record
#             yield fulfillment