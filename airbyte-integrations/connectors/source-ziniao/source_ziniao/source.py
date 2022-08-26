#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime
from abc import abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import requests
import csv
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from dateutil.relativedelta import relativedelta
from io import StringIO

BASE_URL = "https://rpa-server.ziniao.com/erp_report/list"

METHOD_POST = "POST"
METHOD_GET = "GET"
MAX_PAGE_SIZE = 500


'''
获取请求头信息 Get request headers
'''


def get_header(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "token": config["secret_key"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def parse_document(document:str):
    return csv.DictReader(StringIO(document))

def get_url_data(url: str):
    result = requests.get(url)
    document_records = parse_document(result.text)
    results = []
    for item in document_records:
        results.append(item)
    return results

# Basic full refresh stream
class ziniao(HttpStream):
    url_base = BASE_URL
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config_param = config
        self.page = 1
        self.current_page = 1

    @property
    @abstractmethod
    def rpaIdList(self) -> str:
        pass

    @property
    def http_method(self) -> str:
        return METHOD_POST

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.page > self.current_page:
            self.current_page += 1
            return {"page": 1}
        return None

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return get_header(self.config_param)

    def request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                          next_page_token: Mapping[str, Any] = None, ) -> Optional[Mapping]:
        body = {
            "rpaIdList": self.rpaIdList,
            "page": self.current_page,
            "limit": MAX_PAGE_SIZE
        }
        if self.config_param["tunnel_method"]["tunnel_method"] == "PERIODIC":
            days = self.config_param["tunnel_method"]["days"]
            today = datetime.date.today()
            end_time = today.strftime("%Y-%m-%d 00:00:00")
            yesterday = today + relativedelta(days=-1 * days)
            start_time = yesterday.strftime("%Y-%m-%d 00:00:00")
            body["startTime"] = start_time
            body["endTime"] = end_time
        else:
            body["startTime"] = self.config_param["tunnel_method"]["start_time"]
            body["endTime"] = self.config_param["tunnel_method"]["end_time"]
        print(body)
        return {"rpaIdList": [1271], "page": 1, "limit": 500, "startTime": "2022-08-12 00:00:00", "endTime": "2022-08-23 00:00:00"}

    def path(self, **kwargs) -> str:
        return ''

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        respJson = response.json()
        if respJson.get("code") == 0:
            count = respJson.get("data").get("count")
            if count > (MAX_PAGE_SIZE*self.current_page):
                self.page += 1
            results = respJson.get("data").get("result")
            if results is None:
                return []
            for item in results:
                item["data"] = get_url_data(item["url"])
            yield from results
        else:
            raise Exception([{"message": "Failed to obtain data."}])


class business_reports(ziniao):
    rpaIdList = [1271]


# Source
class SourceZiniao(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        header = get_header(config)
        body = {"rpaIdList": [1]}
        result = requests.post(BASE_URL, headers=header, params=body)
        if result.status_code == 200:
            return True, None
        else:
            return False, f"No streams to connect to from source -> {result.text}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [business_reports(config=config)]
