#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import base64
import datetime
from abc import ABC
import csv
from io import BytesIO, StringIO
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import requests
import zipfile
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from dateutil.relativedelta import relativedelta

BASE_URL = "https://marketplace.walmartapis.com"
LIMIT = "200"
MAX_DAYS = 90
DATE_TIME_F = "%Y-%m-%dT00:00:00Z"
TIME_F = "T00:00:00Z"


class WalmartStream(HttpStream, ABC):
    url_base = BASE_URL
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self._authenticator = NoAuth()
        self.config_param = config
        self.nextCursor = None

    @property
    def http_method(self) -> str:
        return "GET"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.nextCursor is not None:
            return {"nextCursor": self.nextCursor}
        return None

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return get_header(self.config_param)

class Inventory(WalmartStream):
    name = "INVENTORY_MULTIPLE_ITEM"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        param = f"?limit=50"
        if self.nextCursor is not None:
            param += f"&nextCursor={self.nextCursor}"
        return f"/v3/inventories{param}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            respJson = response.json()
            results = respJson.get("elements").get("inventories")
            if "nextCursor" not in respJson.get("meta"):
                self.nextCursor = None
            elif respJson.get("meta").get("nextCursor") is not None:
                self.nextCursor = respJson.get("meta").get("nextCursor")
            if results is None:
                return []
            for item in results:
                item["source_name"] = self.config_param["source_name"]
            yield from results
        else:
            raise Exception([{"message": "Failed to obtain data."}])

class Requests(WalmartStream):

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    @property
    def type(self) -> str:
        pass

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"/v3/getReport?type={self.type}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            try:
                zip_file = zipfile.ZipFile(BytesIO(response.content))
            except zipfile.BadZipFile as e:
                self.logger.exception(e)
                self.logger.error(
                    f"Received an invalid zip file in response to URL: {response.request.url}."
                    f"The size of the response body is: {len(response.content)}"
                )
                return []
            for gzip_filename in zip_file.namelist():
                document = parse_document(zip_file.read(gzip_filename))
                results = []
                for item in document:
                    item["source_name"] = self.config_param["source_name"]
                    results.append(item)
                yield from results
        else:
            raise Exception([{"message": "Failed to obtain data."}])

class Inventory(WalmartStream):
    name = "INVENTORY_MULTIPLE_ITEM"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        param = f"?limit=50"
        if self.nextCursor is not None:
            param += f"&nextCursor={self.nextCursor}"
        return f"/v3/inventories{param}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            respJson = response.json()
            results = respJson.get("elements").get("inventories")
            if "nextCursor" not in respJson.get("meta"):
                self.nextCursor = None
            elif respJson.get("meta").get("nextCursor") is not None:
                self.nextCursor = respJson.get("meta").get("nextCursor")
            if results is None:
                return []
            for item in results:
                item["source_name"] = self.config_param["source_name"]
            yield from results
        else:
            raise Exception([{"message": "Failed to obtain data."}])

class Departments(WalmartStream):
    name = "DEPARTMENTS"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "/v3/utilities/taxonomy/departments"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            respJson = response.json()
            results = respJson.get("payload")
            if results is None:
                return []
            for item in results:
                item["source_name"] = self.config_param["source_name"]
            yield from results
        else:
            raise Exception([{"message": "Failed to obtain data."}])

class InventoryWFS(WalmartStream):
    name = "INVENTORY_WFS"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        param = f"?limit=300&offset=0"
        if self.nextCursor is not None:
            param = self.nextCursor
        return f"/v3/fulfillment/inventory{param}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            respJson = response.json()
            results = respJson.get("payload").get("inventory")
            limit = int(respJson.get("headers").get("limit"))
            offset = int(respJson.get("headers").get("offset"))
            totalCount = int(respJson.get("headers").get("totalCount"))
            if totalCount > (limit + offset):
                self.nextCursor = f"?limit=300&offset={limit+offset}"
            else:
                self.nextCursor = None
            if results is None:
                return []
            for item in results:
                item["source_name"] = self.config_param["source_name"]
            yield from results
        else:
            raise Exception([{"message": "Failed to obtain data."}])

class Shipments(WalmartStream):

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    @property
    def dateFlag(self) -> bool:
        pass

    @property
    def requsetPath(self) -> str:
        pass

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        param = self.nextCursor
        if self.nextCursor is None:
            param = f"?limit={LIMIT}&offset=0"
        if self.dateFlag:
            date_map = ge_date(self.config_param)
            param += f"&fromCreateDate={date_map.get('start_time')}&toCreateDate={date_map.get('end_time')}"
        return self.requsetPath+param

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            respJson = response.json()
            results = respJson.get("payload")
            limit = int(respJson.get("headers").get("limit"))
            offset = int(respJson.get("headers").get("offset"))
            totalCount = int(respJson.get("headers").get("totalCount"))
            if totalCount > (limit + offset):
                self.nextCursor = f"?limit={LIMIT}&offset={limit+offset}"
            else:
                self.nextCursor = None
            if results is None:
                return []
            for item in results:
                item["source_name"] = self.config_param["source_name"]
            yield from results
        elif response.status_code == 204:
            return []
        else:
            raise Exception([{"message": "Failed to obtain data."}])

class Items(WalmartStream):
    name = "ITEMS"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config
        self.current_page = 1

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        param = f"?limit={LIMIT}&offset=0"
        if self.nextCursor is not None:
            param = self.nextCursor
        return f"/v3/items{param}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            respJson = response.json()
            results = respJson.get("ItemResponse")
            if int(respJson.get("totalItems")) > (self.current_page * int(LIMIT)):
                self.nextCursor = f"?limit={LIMIT}&offset={self.current_page * int(LIMIT)}"
                self.current_page += 1
            else:
                self.nextCursor = None
            if results is None:
                return []
            for item in results:
                item["source_name"] = self.config_param["source_name"]
            yield from results
        else:
            raise Exception([{"message": "Failed to obtain data."}])


class Returns(WalmartStream):
    name = "RETURNS"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        param = self.nextCursor
        if self.nextCursor is None:
            param = f"?limit={LIMIT}"
            date_map = ge_date(self.config_param)
            param += f"&returnCreationStartDate={date_map.get('start_time')}&returnCreationEndDate={date_map.get('end_time')}"
        return f"/v3/returns{param}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            respJson = response.json()
            results = respJson.get("returnOrders")
            nextCursor = respJson.get("meta").get("nextCursor")
            self.nextCursor = nextCursor
            if results is None:
                return []
            for item in results:
                item["source_name"] = self.config_param["source_name"]
            yield from results
        else:
            raise Exception([{"message": "Failed to obtain data."}])


class Orders(WalmartStream):

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    @property
    def shipNodeType(self) -> str:
        pass

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        param = self.nextCursor
        if self.nextCursor is None:
            param = f"?limit={LIMIT}&shipNodeType={self.shipNodeType}"
            date_map = ge_date(self.config_param)
            param += f"&createdStartDate={date_map.get('start_time')}&createdEndDate={date_map.get('end_time')}"
        return f"/v3/orders{param}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            respJson = response.json()
            results = respJson.get("list").get("elements").get("order")
            nextCursor = respJson.get("list").get("meta").get("nextCursor")
            self.nextCursor = nextCursor
            if results is None:
                return []
            for item in results:
                item["source_name"] = self.config_param["source_name"]
            yield from results
        else:
            raise Exception([{"message": "Failed to obtain data."}])


class OrdersSellerFulfilled(Orders):
    name = "ORDERS_SELLER_FULFILLED"
    shipNodeType = "SellerFulfilled"

class OrdersWFSFulfilled(Orders):
    name = "ORDERS_WFS_FULFILLED"
    shipNodeType = "WFSFulfilled"

class Orders3PLFulfilled(Orders):
    name = "ORDERS_3PL_FULFILLED"
    shipNodeType = "3PLFulfilled"

class InboundShipmentItems(Shipments):
    dateFlag = False
    requsetPath = "/v3/fulfillment/inbound-shipment-items"
    name = "GET_SHIPMENT_ITEMS"

class InboundShipments(Shipments):
    dateFlag = True
    requsetPath = "/v3/fulfillment/inbound-shipments"
    name = "GET_SHIPMENTS"

class ItemRequests(Requests):
    name = "REQUESTS_ITEM"
    type = "item"

class BuyboxRequests(Requests):
    name = "REQUESTS_BUYBOX"
    type = "buybox"

class CpaRequests(Requests):
    name = "REQUESTS_CPA"
    type = "cpa"

class ShippingProgramRequests(Requests):
    name = "REQUESTS_SHIPPING_PROGRAM"
    type = "shippingProgram"

class ShippingConfigurationRequests(Requests):
    name = "REQUESTS_SHIPPING_CONFIGURATION"
    type = "shippingConfiguration"

class ItemPerformanceRequests(Requests):
    name = "REQUESTS_ITEM_PERFORMANCE"
    type = "itemPerformance"

class ReturnOverridesRequests(Requests):
    name = "REQUESTS_RETURN_OVERRIDES"
    type = "returnOverrides"

class PromoRequests(Requests):
    name = "REQUESTS_PROMO"
    type = "promo"

def parse_document(document: bytes):
    return csv.DictReader(StringIO(document.decode()))

def ge_date(config: Mapping[str, Any]) -> Mapping[str, Any]:
    today = datetime.datetime.today()
    if config["tunnel_method"]["tunnel_method"] == "PERIODIC":
        days = config["tunnel_method"]["days"]
        end_time = today.strftime(DATE_TIME_F)
        yesterday = today + relativedelta(days=-1 * days)
        start_time = yesterday.strftime(DATE_TIME_F)
        return {"start_time": start_time, "end_time": end_time}
    else:
        start_time = config["tunnel_method"]["start_time"] + TIME_F
        end_time = today.strftime(DATE_TIME_F)
        if "end_time" in config["tunnel_method"] \
                and config["tunnel_method"]["end_time"] is not None \
                and config["tunnel_method"]["end_time"] != "":
            end_time = config["tunnel_method"]["end_time"] + TIME_F
        else:
            start_date = datetime.datetime.strptime(start_time, DATE_TIME_F)
            temp = (today - start_date).days
            if temp > MAX_DAYS:
                start_time = (today + relativedelta(days=-1 * MAX_DAYS)).strftime(DATE_TIME_F)
        return {"start_time": start_time, "end_time": end_time}

def get_header(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "Authorization": get_authorization(config),
        "WM_SEC.ACCESS_TOKEN": config["access_token"],
        "WM_QOS.CORRELATION_ID": config["source_name"],
        "WM_SVC.NAME": config["source_name"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def get_authorization(config: Mapping[str, Any]) -> Mapping[str, Any]:
    clientId = config["client_id"]
    clientSecret = config["client_secret"]
    en_str = base64.b64encode(bytes(clientId + ":" + clientSecret, 'utf-8'))
    return "Basic " + en_str.decode('utf-8')


def check_token(config: Mapping[str, Any]) -> Mapping[str, Any]:
    header = {
        "Authorization": get_authorization(config),
        "WM_QOS.CORRELATION_ID": config["source_name"],
        "WM_SVC.NAME": config["source_name"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    body = {
        "grant_type": "client_credentials"
    }
    return requests.post(BASE_URL + "/v3/token", headers=header, params=body)


def get_token(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return check_token(config).json().get("access_token")


# Source
class SourceWalmart(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        result = check_token(config)
        if result.status_code == 200:
            return True, None
        else:
            return False, f"No streams to connect to from source -> {result.text}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        access_token = get_token(config)
        config["access_token"] = access_token
        return [OrdersSellerFulfilled(config),
                OrdersWFSFulfilled(config),
                Orders3PLFulfilled(config),
                Departments(config),
                ItemRequests(config),
                BuyboxRequests(config),
                CpaRequests(config),
                # ShippingProgramRequests(config),
                # ShippingConfigurationRequests(config),
                ItemPerformanceRequests(config),
                ReturnOverridesRequests(config),
                PromoRequests(config),
                InboundShipments(config),
                InboundShipmentItems(config),
                Items(config),
                Inventory(config),
                InventoryWFS(config),
                Returns(config)]
