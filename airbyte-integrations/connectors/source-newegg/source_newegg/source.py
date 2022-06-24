#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import datetime
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from dateutil.relativedelta import relativedelta

VERSION = 309
MAX_PAGE_SIZE = 100
BASE_URL = "https://api.newegg.com/marketplace/"
AUTH_URL = "https://api.newegg.com/marketplace/ordermgmt/servicestatus?sellerid=%s"


def get_header(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "Authorization": config["api_key"],
        "SecretKey": config["secret_key"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


class orderinfo(HttpStream):
    url_base = BASE_URL
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config_param = config
        self.page_index = 1
        self.current_page_index = 1

    @property
    def http_method(self) -> str:
        return "PUT"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.page_index > self.current_page_index:
            self.current_page_index += 1
            return {"page_index": 1}
        return None

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None
                        ) -> Mapping[str, Any]:
        return get_header(self.config_param)

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        body = {
            "OperationType": "GetOrderInfoRequest",
            "RequestBody": {
                "PageIndex": self.current_page_index,
                "PageSize": MAX_PAGE_SIZE,
                "RequestCriteria": {}
            }
        }
        if self.config_param["tunnel_method"]["tunnel_method"] == "PERIODIC":
            days = self.config_param["tunnel_method"]["days"]
            today = datetime.date.today()
            end_time = today.strftime("%Y-%m-%d 00:00:00")
            yesterday = today + relativedelta(days=-1*days)
            start_time = yesterday.strftime("%Y-%m-%d 00:00:00")
            body["RequestBody"]["RequestCriteria"] = {
                "OrderDateFrom": start_time,
                "OrderDateTo": end_time
            }
        else:
            body["RequestBody"]["RequestCriteria"] = {
                "OrderDateFrom": self.config_param["tunnel_method"]["start_time"],
                "OrderDateTo": self.config_param["tunnel_method"]["end_time"]
            }
        return body

    def path(self, **kwargs) -> str:
        return f"ordermgmt/order/orderinfo?sellerid={self.config_param['seller_id']}&version={VERSION}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            self.page_index = response.json().get("ResponseBody").get("PageInfo").get("TotalPageCount")
            results = response.json().get("ResponseBody").get("OrderInfoList")
            for item in results:
                item["source_name"] = self.config_param["source_name"]
            yield from results
        else:
            raise Exception([{"message": "Only AES decryption is implemented."}])


# Source
class SourceNewegg(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth_url = AUTH_URL % config["seller_id"]
        header = get_header(config)
        result = requests.get(auth_url, headers=header)
        if result.status_code == 200:
            return True, None
        else:
            return False, f"No streams to connect to from source -> {result.text}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [orderinfo(config=config)]
