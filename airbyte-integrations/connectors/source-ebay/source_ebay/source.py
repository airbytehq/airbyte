#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import base64
import datetime
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from dateutil.relativedelta import relativedelta

AUTH_BASE_URL = "https://api.ebay.com"
BASE_URL = "https://apiz.ebay.com"
SCOPE = "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly https://api.ebay.com/oauth/api_scope/sell.finances https://api.ebay.com/oauth/api_scope/sell.payment.dispute https://api.ebay.com/oauth/api_scope/commerce.identity.readonly https://api.ebay.com/oauth/api_scope/commerce.notification.subscription https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly"
DATE_TIME_F = "%Y-%m-%dT00:00:00Z"
DATE_TIME_F_S = "%Y-%m-%dT00:00:01.000Z"
MAX_DAYS = 90
TIME_F = "T00:00:00Z"

class EbayStream(HttpStream, ABC):
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self._authenticator = NoAuth()
        self.config_param = config
        self.nextCursor = None

    @property
    def limit(self) -> str:
        pass
    @property
    def dataParam(self) -> str:
        pass
    @property
    def dateParam(self) -> str:
        pass
    @property
    def basePath(self) -> str:
        pass
    @property
    def dateFormat(self) -> str:
        pass
    @property
    def dateFilter(self) -> bool:
        pass

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.nextCursor is not None:
            return {"nextCursor": self.nextCursor}
        return None

    @property
    def http_method(self) -> str:
        return "GET"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        date_map = ge_date(self.config_param, self.dateFormat)
        param = f"limit={self.limit}"
        if self.dateFilter:
            param += f"&filter={self.dateParam}:[{date_map.get('start_time')}..{date_map.get('end_time')}]"
        if self.nextCursor is not None:
            param = self.nextCursor
        return f"{self.basePath}?{param}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            respJson = response.json()
            results = respJson.get(self.dataParam)
            if "next" in respJson:
                self.nextCursor = str(respJson.get("next")).split('?')[1]
            else:
                self.nextCursor = None
            if results is None:
                return []
            for item in results:
                item["source_name"] = self.config_param["source_name"]
            yield from results
        elif response.status_code == 204:
            yield from []
        else:
            raise Exception([{"message": "Failed to obtain data."}])

class Inventory(EbayStream):
    dateFilter = False
    dateFormat = DATE_TIME_F
    url_base = AUTH_BASE_URL
    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return get_header(self.config_param)

class Fulfillment(EbayStream):
    dateFilter = True
    dateFormat = DATE_TIME_F_S
    url_base = AUTH_BASE_URL
    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return get_header(self.config_param)


class Finances(EbayStream):
    dateFilter = True
    dateFormat = DATE_TIME_F
    url_base = BASE_URL
    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        headers = get_header(self.config_param)
        headers["X-EBAY-C-MARKETPLACE-ID"] = self.config_param['marketplace_id']
        return headers

class Marketing(EbayStream):
    dateFilter = False
    dateFormat = DATE_TIME_F_S
    url_base = AUTH_BASE_URL
    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.config_param = config

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return get_header(self.config_param)

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        param = f"limit={self.limit}&marketplace_id={self.config_param['marketplace_id']}"
        if self.nextCursor is not None:
            param = self.nextCursor
        return f"{self.basePath}?{param}"

class PromotionReport(Marketing):
    limit = 200
    name = "GET_PROMOTION_REPORTS"
    dataParam = "promotionReports"
    dateParam = "promotionReports"
    basePath = "/sell/marketing/v1/promotion_report"

class Promotion(Marketing):
    limit = 200
    name = "GET_PROMOTIONS"
    dataParam = "promotions"
    dateParam = "promotions"
    basePath = "/sell/marketing/v1/promotion"

class Campaigns(Inventory):
    limit = 500
    name = "GET_CAMPAIGNS"
    dataParam = "campaigns"
    dateParam = "campaigns"
    basePath = "/sell/marketing/v1/ad_campaign"

class InventoryItems(Inventory):
    limit = 100
    name = "GET_INVENTORY_ITEMS"
    dataParam = "inventoryItems"
    dateParam = "inventoryItems"
    basePath = "/sell/inventory/v1/inventory_item"

class InventoryLocations(Inventory):
    limit = 100
    name = "GET_INVENTORY_LOCATIONS"
    dataParam = "locations"
    dateParam = "locations"
    basePath = "/sell/inventory/v1/location"

class Orders(Fulfillment):
    limit = 200
    name = "GET_ORDERS"
    dataParam = "orders"
    dateParam = "creationdate"
    basePath = "/sell/fulfillment/v1/order"

class Transaction(Finances):
    limit = 1000
    name = "GET_TRANSACTIONS"
    dataParam = "transactions"
    dateParam = "transactionDate"
    basePath = "/sell/finances/v1/transaction"

class Payout(Finances):
    limit = 200
    name = "GET_PAYOUTS"
    dataParam = "payouts"
    dateParam = "payoutDate"
    basePath = "/sell/finances/v1/payout"

def ge_date(config: Mapping[str, Any], dateFormat: str) -> Mapping[str, Any]:
    time_f = "T"+dateFormat.split("T")[1]
    today = datetime.datetime.today()
    if config["tunnel_method"]["tunnel_method"] == "PERIODIC":
        days = config["tunnel_method"]["days"]
        end_time = today.strftime(dateFormat)
        yesterday = today + relativedelta(days=-1 * days)
        start_time = yesterday.strftime(dateFormat)
        return {"start_time": start_time, "end_time": end_time}
    else:
        start_time = config["tunnel_method"]["start_time"] + time_f
        end_time = today.strftime(dateFormat)
        if "end_time" in config["tunnel_method"] \
                and config["tunnel_method"]["end_time"] is not None \
                and config["tunnel_method"]["end_time"] != "":
            end_time = config["tunnel_method"]["end_time"] + time_f
        else:
            start_date = datetime.datetime.strptime(start_time, dateFormat)
            temp = (today - start_date).days
            if temp > MAX_DAYS:
                start_time = (today + relativedelta(days=-1 * MAX_DAYS)).strftime(dateFormat)
        return {"start_time": start_time, "end_time": end_time}

def get_header(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "Authorization": f"Bearer {config['access_token']}",
        "Accept": "application/json"
    }

def get_authorization(config: Mapping[str, Any]) -> Mapping[str, Any]:
    clientId = config["client_id"]
    clientSecret = config["client_secret"]
    en_str = base64.b64encode(bytes(clientId + ":" + clientSecret, 'utf-8'))
    return "Basic " + en_str.decode('utf-8')

def get_access_token(config: Mapping[str, Any]) -> Mapping[str, Any]:
    header = {
        "Authorization": get_authorization(config),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "grant_type": "refresh_token",
        "refresh_token": config["refresh_token"],
        "scope": SCOPE
    }
    return requests.post(AUTH_BASE_URL + "/identity/v1/oauth2/token", headers=header, params=body)


# Source
class SourceEbay(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        result = get_access_token(config)
        if result.status_code == 200:
            return True, None
        else:
            return False, f"No streams to connect to from source -> {result.text}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["access_token"] = get_access_token(config).json().get("access_token")
        return [Transaction(config),
                Payout(config),
                Orders(config),
                InventoryItems(config),
                InventoryLocations(config),
                Campaigns(config),
                PromotionReport(config),
                Promotion(config)
                ]
