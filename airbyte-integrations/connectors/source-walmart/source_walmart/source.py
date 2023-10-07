#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256, MD5
import uuid

import json
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
DATE_TIME_F = "%Y-%m-%dT00:00:00.000Z"
TIME_F = "T00:00:00.000Z"


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

    @property
    def raise_on_http_errors(self) -> bool:
        return False

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.nextCursor is not None:
            return {"nextCursor": self.nextCursor}
        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        url = BASE_URL + self.path()
        header = get_header(self.config_param, url, self.http_method)

        return header



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
        return self.requsetPath + param

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

        if "CA" == self.config_param.get("region"):
            return f"/v3/ca/items{param}"
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
        region = self.config_param.get("region")
        if self.nextCursor is None:
            if "US" == region:
                param = f"?limit={LIMIT}&shipNodeType={self.shipNodeType}"
            else:
                param = f"?limit={LIMIT}"
            date_map = ge_date(self.config_param)
            param += f"&createdStartDate={date_map.get('start_time')}"

        if "CA" == region:
            if "WFSFulfilled" == self.shipNodeType:
                return f"/v3/ca/orders/wfs{param}"
            else:
                return f"/v3/ca/orders{param}"
        else:
            return f"/v3/orders{param}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        region = self.config_param.get("region")


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
        elif "CA" == region and response.status_code == 404:
            self.logger.warning(response.text)
            return []

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


def sha256_with_rsa_sign(privatekey, message):
    private_key = RSA.importKey(base64.b64decode(privatekey.encode("utf-8")))
    cipher = PKCS1_v1_5.new(private_key)
    h = SHA256.new(message.encode("utf-8"))
    signature = cipher.sign(h)
    return base64.b64encode(signature)


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
        if (
            "end_time" in config["tunnel_method"]
            and config["tunnel_method"]["end_time"] is not None
            and config["tunnel_method"]["end_time"] != ""
        ):
            end_time = config["tunnel_method"]["end_time"] + TIME_F
        else:
            start_date = datetime.datetime.strptime(start_time, DATE_TIME_F)
            temp = (today - start_date).days
            if temp > MAX_DAYS:
                start_time = (today + relativedelta(days=-1 * MAX_DAYS)).strftime(DATE_TIME_F)
        return {"start_time": start_time, "end_time": end_time}


def getTimestamp():
    timestamp = datetime.datetime.now().timestamp()
    timestamp = timestamp * 1000
    return int(timestamp)


def get_header(config: Mapping[str, Any], url: str, method: str) -> Mapping[str, Any]:
    if "CA" == config["region"]:
        consumer_id = config["client_id"]
        private_key = config["client_secret"]
        correlation_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, config["source_name"]))
        wm_svc_name = MD5.MD5Hash.new(config["source_name"]).hexdigest()
        timestamp = str(getTimestamp())
        # url = "https://marketplace.walmartapis.com/v3/ca/orders?createdStartDate=2023-09-01T00:00:00.000Z&limit=200"
        # timestamp = "1695612950840"
        string_to_sign = f"{consumer_id}\n{url}\n{method}\n{timestamp}\n"
        auth_signature = sha256_with_rsa_sign(private_key, string_to_sign).decode("utf-8")
        return {
            "WM_CONSUMER.CHANNEL.TYPE": config["channel_type"],
            "WM_SVC.NAME": wm_svc_name,
            "WM_QOS.CORRELATION_ID": correlation_id,
            "WM_SEC.TIMESTAMP": timestamp,
            "WM_SEC.AUTH_SIGNATURE": auth_signature,
            "WM_CONSUMER.ID": consumer_id,
            "Accept": "application/json",
            "WM_TENANT_ID": "WALMART.CA",
            "WM_LOCALE_ID": "en_CA",
        }

    else:
        return {
            "Authorization": get_authorization(config),
            "WM_SEC.ACCESS_TOKEN": get_token(config),
            "WM_QOS.CORRELATION_ID": config["source_name"],
            "WM_SVC.NAME": config["source_name"],
            "Content-Type": "application/json",
            "Accept": "application/json",
        }


def get_authorization(config: Mapping[str, Any]) -> Mapping[str, Any]:
    clientId = config["client_id"]
    clientSecret = config["client_secret"]
    en_str = base64.b64encode(bytes(clientId + ":" + clientSecret, "utf-8"))
    return "Basic " + en_str.decode("utf-8")


def check_token(config: Mapping[str, Any]) -> Mapping[str, Any]:
    header = {
        "Authorization": get_authorization(config),
        "WM_QOS.CORRELATION_ID": config["source_name"],
        "WM_SVC.NAME": config["source_name"],
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {"grant_type": "client_credentials"}
    return requests.post(BASE_URL + "/v3/token", headers=header, params=body)


def get_token(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return check_token(config).json().get("access_token")


def get_ca_item(config: Mapping[str, Any]) -> Mapping[str, Any]:
    url = BASE_URL + "/v3/ca/items"
    header = get_header(config, url=url, method="GET")
    body = {"grant_type": "client_credentials"}
    return requests.get(url, headers=header)


# Source
class SourceWalmart(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        if "CA" == config["region"]:
            result = get_ca_item(config)
            if result.status_code == 200:
                return True, None
            else:
                return False, f"No streams to connect to from source -> {result.text}"
        else:
            result = check_token(config)
            if result.status_code == 200:
                return True, None
            else:
                return False, f"No streams to connect to from source -> {result.text}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams: list = [OrdersSellerFulfilled(config), OrdersWFSFulfilled(config), Items(config)]
        if "US" == config["region"]:
            streams.append(Orders3PLFulfilled(config))
            streams.append(Departments(config))
            streams.append(InboundShipments(config))
            streams.append(InboundShipmentItems(config))
            streams.append(Inventory(config))
            streams.append(InventoryWFS(config))
            streams.append(Returns(config))

        return streams
