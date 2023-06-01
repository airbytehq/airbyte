#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import base64
import random
import string
import hashlib
from datetime import datetime
import hmac
import requests
from dateutil.relativedelta import relativedelta

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


BASE_URL = "https://openapi.sheincorp.com"
# BASE_URL = "https://openapi-test01.sheincorp.cn"
ORDER_LIST_PATH = "/open-api/order/order-list"
ORDER_DETAIL_PATH = "/open-api/order/order-detail"
EXPORT_ADDRESS_PATH = "/open-api/order/export-address"

METHOD_POST = "POST"
METHOD_GET = "GET"
MAX_PAGE_SIZE = 30


'''
获取当前时间戳
'''
def getTimestamp():
    timestamp = datetime.now().timestamp()
    timestamp = timestamp * 1000
    return int(timestamp)

'''
获取5位随机字符串
'''
def genRandomString(slen=5):
    return ''.join(random.sample(string.ascii_letters + string.digits, slen))

'''
获取请求头信息 Get request headers
'''
def get_header(open_key_id:str, secret_key:str, path:str) -> Mapping[str, Any]:

    timestamp = getTimestamp()
    randomKey = genRandomString()
    value = "{}&{}&{}".format(open_key_id, str(timestamp), path)
    key = "{}{}".format(secret_key, randomKey)
    digest = hmac.new(key.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()
    base64Str = str(base64.b64encode(digest.encode()), 'utf-8')
    signature = "{}{}".format(randomKey, base64Str)

    return {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json",
        "x-lt-openKeyId": open_key_id,
        "x-lt-timestamp": str(timestamp),
        "x-lt-signature": signature
    }


def order_detail(config, orderNo):
    url_base = BASE_URL + ORDER_DETAIL_PATH
    headers = get_header(config["open_key_id"], config["secret_key"], ORDER_DETAIL_PATH)
    body = {
        "orderNoList": [
            orderNo
        ]
    }
    resp = requests.post(url_base, headers=headers, json=body)
    resp_json = resp.json()
    if resp_json.get("code") == "0":
        return resp_json.get("info")[0]
    return None

def export_address(config, orderNo):
    url_base = BASE_URL + EXPORT_ADDRESS_PATH
    headers = get_header(config["open_key_id"], config["secret_key"], EXPORT_ADDRESS_PATH)
    body = {
        "orderNo": orderNo,
        "handleType": 1
    }
    resp = requests.request("post", url_base, headers=headers, json=body)
    resp_json = resp.json()
    if resp_json.get("code") == "0":
        return resp_json.get("info")
    return None



class order_list(HttpStream):
    url_base = BASE_URL + ORDER_LIST_PATH
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config_param = config
        self.page = 1
        self.current_page = 1
        self.orderNo = None

    @property
    def http_method(self) -> str:
        return "POST"

    def path(self, **kwargs) -> str:
        return ORDER_LIST_PATH

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.page > self.current_page:
            self.current_page += 1
            return {"page": 1}
        return None

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return get_header(self.config_param["open_key_id"], self.config_param["secret_key"], ORDER_LIST_PATH)

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        body = {
            "queryType": 2,
            "startTime": "2023-05-08 16:20:33",
            "endTime": "2023-05-29 10:23:50",
            "page": 1,
            "pageSize": 30
        }
        if self.config_param["tunnel_method"]["tunnel_method"] == "PERIODIC":
            days = self.config_param["tunnel_method"]["days"]
            today = datetime.today()
            end_time = today.strftime("%Y-%m-%d 00:00:00")
            yesterday = today + relativedelta(days=-1 * days)
            start_time = yesterday.strftime("%Y-%m-%d 00:00:00")
            body["startTime"] = start_time
            body["endTime"] = end_time
        else:
            body["startTime"] = self.config_param["tunnel_method"]["start_time"]
            body["endTime"] = self.config_param["tunnel_method"]["end_time"]
        return body

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        respJson = response.json()
        if respJson.get("code") == "0":
            count = respJson.get("info").get("count")
            if count > (MAX_PAGE_SIZE * self.current_page):
                self.page += 1
            results = respJson.get("info").get("orderList")
            ret_list = []
            if results is None:
                return []
            for item in results:
                orderNo = item["orderNo"]
                orderCreateTime = item["orderCreateTime"]
                orderUpdateTime = item["orderUpdateTime"]
                item = order_detail(self.config_param, orderNo)
                # item["order_info"] = order_detail(self.config_param, item["orderNo"])
                addr = export_address(self.config_param, orderNo)
                item["receiveMsgList"] = addr
                item["source_name"] = self.config_param["source_name"]
                item["orderCreateTime"] = orderCreateTime
                item["orderUpdateTime"] = orderUpdateTime
                ret_list.append(item)
            # yield from results
            return ret_list
        else:
            raise Exception([{"message": "Failed to obtain data.", "msg": response.text}])



# Source
class SourceShein(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:

        headers = get_header(config["open_key_id"], config["secret_key"], ORDER_LIST_PATH)
        today = datetime.today()
        end_time = today.strftime("%Y-%m-%d %H:%M:%S")
        yesterday = today + relativedelta(days=-1 * 5)
        start_time = yesterday.strftime("%Y-%m-%d 00:00:00")
        body = {
            "queryType": 2,
            "startTime": start_time,
            "endTime": end_time,
            "page": 1,
            "pageSize": 30
        }
        url = BASE_URL+ORDER_LIST_PATH
        resp = requests.post(url, headers=headers, json=body)
        resp_json = resp.json()
        if resp_json.get("code") == '0':
            return True, None
        else:
            return False, f"No streams to connect to from source -> {resp.text}"


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [order_list(config=config)]
