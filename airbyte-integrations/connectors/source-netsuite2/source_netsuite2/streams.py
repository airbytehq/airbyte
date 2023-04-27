# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from datetime import datetime
import logging
import json

import requests
import uuid
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from requests_oauthlib import OAuth1
from source_netsuite2.constraints import INCREMENTAL_CURSOR, RECORD_PATH, REST_PATH

class NetSuiteStream(HttpStream, ABC):
    def __init__(
    self,
    auth: OAuth1,
    base_url: str,
    start_datetime: str,
    window_in_days: int,
    object_names: List[str],
    ):
        self.base_url = base_url
        self.start_datetime = start_datetime
        self.window_in_days = window_in_days
        self.object_names = object_names
        super().__init__(authenticator=auth)

    primary_key = "id"

    http_method = "POST"

    records_per_slice = 100

    request_limit = 1000 # TODO: change to 1000

    raise_on_http_errors = True

    total_records = 0

    @property
    def url_base(self) -> str:
        return self.base_url
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp = response.json()
        has_more = resp.get("hasMore")
        if has_more:
            return {"offset": resp["offset"] + resp["count"]}
        return None

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"limit": self.request_limit}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
         return {"prefer": "transient", "Content-Type": "application/json"}

class IncrementalNetsuiteStream(NetSuiteStream, IncrementalMixin):
    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return self.records_per_slice

    @property
    def cursor_field(self) -> str:
        return INCREMENTAL_CURSOR
    
    @abstractproperty
    def path(self, **kwargs) -> str:
        pass   

    @property
    def state(self) -> Mapping[str, Any]:
        if hasattr(self, "_state"):
            return self._state
        else:
            return {self.cursor_field: self.start_datetime}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        if hasattr(self, "_state"):
             self._state = {self.cursor_field: value[self.cursor_field]}
        else:
            self._state = {self.cursor_field: value[self.cursor_field]}

    @abstractmethod
    def request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Optional[Mapping]:
        pass

    @abstractmethod
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        pass

class Transactions(IncrementalNetsuiteStream):

    def path(self, **kwargs) -> str:
        return REST_PATH + "query/v1/suiteql"

    def request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Optional[Mapping]:
        current_cursor = stream_state.get(self.cursor_field, self.start_datetime)
        date_object_cursor = datetime.strptime(current_cursor, '%Y-%m-%dT%H:%M:%SZ')
        formated_cursor = date_object_cursor.strftime("%Y-%m-%d %H:%M:%S")
        tuple_repr = tuple(self.object_names)
        commaSeparatedObjectNames = str(tuple_repr)
        return {
	        "q": "SELECT id, tranid, BUILTIN.DF(type) as type, to_char(lastModifiedDate, 'yyyy-mm-dd HH24:MI:SS') as lastModifiedDate FROM transaction as t WHERE  t.type IN (" + commaSeparatedObjectNames + ") AND to_char(lastModifiedDate, 'yyyy-mm-dd HH24:MI:SS') > '" + formated_cursor + "' ORDER BY lastModifiedDate ASC"
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("items")
    
    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            record_type = record.get("type").replace(" ", "").lower()
            if record_type == "payment":
                record_type = "customerpayment"
            url = self.base_url + RECORD_PATH + record_type + "/" + record.get("id")
            args = {"method": "GET", "url": url, "params": {"expandSubResources": True}}
            prep_req = self._session.prepare_request(requests.Request(**args))
            response = self._send_request(prep_req, request_kwargs={})
            if response.status_code == requests.codes.ok:
                transactionRecord = response.json()
                transactionRecord_with_type = {**transactionRecord, "type": record_type}
                self.logger.info(f"Fetched record {transactionRecord_with_type.get('id')} with datelastmodified {transactionRecord_with_type.get(self.cursor_field)}")
                self.state = transactionRecord_with_type
                self.logger.info(f"Current state is {self.state}")
                yield transactionRecord_with_type
            


class InventorySnapshot(NetSuiteStream):

    def path(self, **kwargs) -> str:
        return REST_PATH + "query/v1/suiteql"

    def request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Optional[Mapping]:
        importid = str(uuid.uuid4())
        return {
	        "q": "SELECT id,itemid, BUILTIN.DF(itemtype) as type, to_char(lastModifiedDate, 'yyyy-mm-dd HH24:MI:SS') as lastModifiedDate, '" + importid + "' as importid FROM item where itemtype IN ('InvtPart','Assembly') and isinactive = 'F'"
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("items")

    
    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            currentImportId = record.get("importid")
            record_type = record.get("type").replace(" ", "").lower()
            if (record_type.startswith("assembly")):
                record_type = "assemblyitem"
            url = self.base_url + RECORD_PATH + record_type + "/" + record.get("id")
            args = {"method": "GET", "url": url, "params": {"expandSubResources": True}}
            prep_req = self._session.prepare_request(requests.Request(**args))
            response = self._send_request(prep_req, request_kwargs={})
            if response.status_code == requests.codes.ok:
                itemRecord = response.json()
                itemLocations = itemRecord.get("locations").get("items")
                itemMembersObject = itemRecord.get("member", None)
                itemMembers = itemMembersObject.get("items") if itemMembersObject else None
                itemPricing = itemRecord.get("price", None).get("items") if itemRecord.get("price", None) else None

                cleaned_itemMembers = []
                if itemMembers:
                    for itemMember in itemMembers:
                        cleaned_item_member = {
                            'memberItemId': itemMember.get('item').get('id', None),
                            'memberItemRefName': itemMember.get('item').get('refName', None),
                            'memberQuantity': itemMember['quantity'],
                            'lineNumber': itemMember.get('lineNumber', None),
                            'itemSource': itemMember.get('itemSource', None)

                        }
                    cleaned_itemMembers.append(itemMember)   
                
                cleaned_prices = []
                for price in itemPricing:
                    cleaned_price = {
                        'price': price.get('price'),
                        'priceLevelRefName': price.get('priceLevelName'),
                        "priceLevelId": price.get('priceLevel').get('id')

                    }
                    cleaned_prices.append(cleaned_price)

                cleaned_itemLocations = []
                for location in itemLocations:
                    cleaned_item_location = {
                        'locationId': location['locationId'],
                        'location_display': location['location_display'],
                        'quantityAvailable': location.get('quantityAvailable', None),
                        'averageCostMli': location.get('averageCostMli', None),
                        'lastPurchasePriceMli': location.get('lastPurchasePriceMli', None),
                        'onHandValueMli': location.get('onHandValueMli', None),
                        'quantityCommitted': location.get('quantityCommitted', None),
                        'quantityOnHand': location.get('quantityOnHand', None),
                        'quantityOnOrder': location.get('quantityOnOrder', None)
                    }
                    cleaned_itemLocations.append(cleaned_item_location)
                
                itemRecord_with_type = {
                        "importId": currentImportId
                    , "internalId": itemRecord.get("internalId")
                    , "id": itemRecord.get("internalId")
                    , "itemId": itemRecord.get("itemId")
                    , "type": record_type
                    , "locations": itemRecord.get("locations").get("items")
                    , "lastModifiedDate": record.get("lastmodifieddate")
                    , "salesDescription": itemRecord.get("salesDescription")
                    , "lastPurchasePrice": itemRecord.get("lastPurchasePrice")
                    , "manufacturer": itemRecord.get("manufacturer")
                    , "totalValue": itemRecord.get("totalValue")
                    , "quantityOnHand": itemRecord.get("quantityOnHand")
                    , "quantityOnOrder": itemRecord.get("quantityOnOrder")
                    , "locations": cleaned_itemLocations
                    , "member": cleaned_itemMembers
                    , "price": cleaned_prices
                    }
                yield itemRecord_with_type
    



