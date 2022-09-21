#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import base64
import requests
import xmltodict
from datetime import datetime, timedelta
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

class BaseClass(HttpStream):

    def __init__(self, **kwargs):
        super().__init__()
        self._cursor_value = 0
        self._count_value = 0
        self._final_page_checker = False 

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response = response.json()
        count = response["count"]
        
        print(f"COUNT: {count}")
        
        if count == 0 and self._final_page_checker == True: 
            # If the last page was already processed (read the coment below), then the pagination has finished.
            return None
        elif count == 0: 
            # If count = 0, then it's the last page, but it will run one more execution using the previous cursor value - 1.
            self._final_page_checker = True
            return self._count_value 
        else: 
            # If pagination didn't finish yet, then the cursor value will continue incrementing normally.
            self._count_value = count
            return self._count_value 


    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ):
        params = {"cursor":self._cursor_value, "limit":50}

        if self._final_page_checker == True and self._count_value == 1:
            # If the last pages were already processed, the count returned will be 1. So, we process the last page and the execution finishes.
            new_cursor = params["cursor"] + self._count_value
        elif self._final_page_checker == True:
            # Using the previous cursor value, which returned the last page, but summing it with -1, to get the data from the last pages.
            new_cursor = params["cursor"] - 1
        else:
            # Pagination didn't finish yet, then the cursor value will continue incrementing normally.
            new_cursor = params["cursor"] + self._count_value 
        
        self._cursor_value = new_cursor
        params["cursor"] = new_cursor

        print(f"CURSOR: {new_cursor}")
        return params
    
    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):
        response = response.json()
        items = []

        for item in response['data']:

            item["xml"] = base64.b64decode(item["xml"])            
            xml_to_dict = xmltodict.parse(item["xml"])
            item["xml"] = xml_to_dict

            invoice = self.format_xml(item)
            items.append(invoice)

        # print(items)
        # with open('./converted_received.json', 'w+') as f:
        #     json.dump(items, f)
        #     f.truncate()
        return items


class NfeReceived(BaseClass):

    url_base = "https://api.arquivei.com.br/v1/"
    primary_key = "invoice_id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config["api_key"]
        self.api_id = config["api_id"]
        self.merchant = config["merchant"]
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "nfe/received"
    
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"X-API-ID": self.api_id, "X-API-KEY": self.api_key, "content-type":"application/json"}
    
    def format_xml(
        self,
        xml_item: Mapping[str, Any]
    ) -> str:
        
        invoice = {
            "data": xml_item["xml"],
            "merchant": self.merchant.upper(),
            "source": "BR_ARQUIVEI",
            "type": f"{self.merchant.lower()}_invoice",
            "id": "NFe" + xml_item["access_key"],
            "timeline": "historic",
            "invoice_id": "NFe" + xml_item["access_key"],
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "cnpjs": [],
            "invoice_type": "inbound",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "sensible": True
        }
        return invoice


class NfeEmitted(BaseClass):

    url_base = "https://api.arquivei.com.br/v1/"
    primary_key = "invoice_id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config["api_key"]
        self.api_id = config["api_id"]
        self.merchant = config["merchant"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "nfe/emitted" 
    
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"X-API-ID": self.api_id, "X-API-KEY": self.api_key, "content-type":"application/json"}

    def format_xml(
        self,
        xml_item: Mapping[str, Any]
    ) -> str:
        
        invoice = {
            "data": xml_item["xml"],
            "merchant": self.merchant.upper(),
            "source": "BR_ARQUIVEI",
            "type": f"{self.merchant.lower()}_invoice",
            "id": "NFe" + xml_item["access_key"],
            "timeline": "historic",
            "invoice_id": "NFe" + xml_item["access_key"],
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "cnpjs": [],
            "invoice_type": "outbound",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "sensible": True
        }
        return invoice


class NfeEvents(BaseClass):

    url_base = "https://api.arquivei.com.br/v1/"
    primary_key = "event_id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config["api_key"]
        self.api_id = config["api_id"]
        self.merchant = config["merchant"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "events/nfe" 
    
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"X-API-ID": self.api_id, "X-API-KEY": self.api_key, "content-type":"application/json"}

    def format_xml(
        self,
        xml_item: Mapping[str, Any]
    ) -> str:
        
        invoice = {
            "data": xml_item["xml"],
            "merchant": self.merchant.upper(),
            "source": "BR_ARQUIVEI",
            "type": f"{self.merchant.lower()}_event_invoice",
            "id": "NFe" + xml_item["access_key"],
            "timeline": "historic",
            "invoice_id": "NFe" + xml_item["access_key"],
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "cnpjs": [],
            "invoice_type": "nfe_event",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "sensible": True
        }
        return invoice


class Cte(BaseClass):

    url_base = "https://api.arquivei.com.br/v1/"
    primary_key = "cte_id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config["api_key"]
        self.api_id = config["api_id"]
        self.merchant = config["merchant"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "cte/taker" 
    
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"X-API-ID": self.api_id, "X-API-KEY": self.api_key, "content-type":"application/json"}

    def format_xml(
        self,
        xml_item: Mapping[str, Any]
    ) -> str:
        
        invoice = {
            "data": xml_item["xml"],
            "merchant": self.merchant.upper(),
            "source": "BR_ARQUIVEI",
            "type": f"{self.merchant.lower()}_cte",
            "id": "CTe" + xml_item["access_key"],
            "timeline": "historic",
            "invoice_id": "CTe" + xml_item["access_key"],
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "cnpjs": [],
            "invoice_type": "cte",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "sensible": True
        }
        return invoice


class CteEvents(BaseClass):

    url_base = "https://api.arquivei.com.br/v2/"
    primary_key = "event_id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.api_key = config["api_key"]
        self.api_id = config["api_id"]
        self.merchant = config["merchant"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "cte/events" 
    
    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"X-API-ID": self.api_id, "X-API-KEY": self.api_key, "content-type":"application/json"}

    def format_xml(
        self,
        xml_item: Mapping[str, Any]
    ) -> str:
        
        invoice = {
            "data": xml_item["xml"],
            "merchant": self.merchant.upper(),
            "source": "BR_ARQUIVEI",
            "type": f"{self.merchant.lower()}_event_cte",
            "id": "CTe" + xml_item["access_key"],
            "timeline": "historic",
            "invoice_id": "CTe" + xml_item["access_key"],
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "cnpjs": [],
            "invoice_type": "cte_event",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "sensible": True
        }
        return invoice


class SourceArquivei(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            
            headers = {
                "X-API-ID": config["api_id"],
                "X-API-KEY": config["api_key"],
                "content-type":"application/json"
            }

            result = requests.get('https://api.arquivei.com.br/v1/nfe/received', headers=headers)
            
            status = result.status_code
            logger.info(f"Ping response code: {status}")
            if status == 200:
                return True, None
            else:
                return False, result
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # NoAuth just means there is no authentication required for this API. It's only included for completeness
        # of the example, but if you don't need authentication, you don't need to pass an authenticator at all.
        # Other authenticators are available for API token-based auth and Oauth2.
        auth = NoAuth()

        return [
            NfeReceived(authenticator=auth, config=config),
            NfeEmitted(authenticator=auth, config=config),
            NfeEvents(authenticator=auth, config=config),
            Cte(authenticator=auth, config=config),
            CteEvents(authenticator=auth, config=config)
        ]
