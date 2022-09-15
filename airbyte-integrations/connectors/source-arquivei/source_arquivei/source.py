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


class NfeReceived(HttpStream):

    url_base = "https://api.arquivei.com.br/v1/"
    primary_key = "invoice_id"

    def __init__(self, config: Mapping[str, Any], start_date: datetime, **kwargs):
        super().__init__()
        self.api_key = config["api_key"]
        self.api_id = config["api_id"]
        self.start_date = start_date
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

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "nfe/received"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"X-API-ID": self.api_id, "X-API-KEY": self.api_key, "content-type":"application/json"}

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
    
    def format_xml(
        self,
        xml_item: Mapping[str, Any]
    ) -> str:
        # TODO: Find a way to remove hardcoded merchant
        merchant = "brmms"
        # xml_item["xml"]["nfeProc"]["NFe"]["infNFe"]["ide"]["dhEmi"],
        invoice = {
            "data": xml_item["xml"],
            "merchant": merchant.upper(),
            "source": "BR_ARQUIVEI",
            "type": f"{merchant}_notafiscal",
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

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):
        response = response.json()
        invoices = []

        for item in response['data']:

            item["xml"] = base64.b64decode(item["xml"])            
            xml_to_dict = xmltodict.parse(item["xml"])
            item["xml"] = xml_to_dict

            invoice = self.format_xml(item)
            invoices.append(invoice)

        # print(invoices)
        # with open('./converted_received.json', 'w+') as f:
        #     json.dump(response, f)
        #     f.truncate()
        return invoices


class Events(HttpStream):

    url_base = "https://api.arquivei.com.br/v1/"
    primary_key = "event_id"


    def __init__(self, config: Mapping[str, Any], start_date: datetime, **kwargs):
        super().__init__()
        self.api_key = config["api_key"]
        self.api_id = config["api_id"]
        self.start_date = start_date
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

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "events/nfe" 

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"X-API-ID": self.api_id, "X-API-KEY": self.api_key, "content-type":"application/json"}


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

    def format_xml(
        self,
        xml_item: Mapping[str, Any]
    ) -> str:
        # TODO: Find a way to remove hardcoded merchant
        merchant = "brmms"
        # xml_item["xml"]["nfeProc"]["NFe"]["infNFe"]["ide"]["dhEmi"],
        invoice = {
            "data": xml_item["xml"],
            "merchant": merchant.upper(),
            "source": "BR_ARQUIVEI",
            "type": f"{merchant}_notafiscal",
            "id": "NFe" + xml_item["access_key"],
            "timeline": "historic",
            "invoice_id": "NFe" + xml_item["access_key"],
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "cnpjs": [],
            "invoice_type": "event",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "sensible": True
        }
        return invoice

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):
        response = response.json()
        invoices = []

        for item in response['data']:

            item["xml"] = base64.b64decode(item["xml"])            
            xml_to_dict = xmltodict.parse(item["xml"])
            item["xml"] = xml_to_dict

            invoice = self.format_xml(item)
            invoices.append(invoice)

        # print(invoices)
        # with open('./converted_events.json', 'w+') as f:
        #     json.dump(response, f)
        #     f.truncate()
        return invoices


class NfeEmitted(HttpStream):

    url_base = "https://api.arquivei.com.br/v1/"
    primary_key = "invoice_id"

    def __init__(self, config: Mapping[str, Any], start_date: datetime, **kwargs):
        super().__init__()
        self.api_key = config["api_key"]
        self.api_id = config["api_id"]
        self.start_date = start_date
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

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "nfe/emitted" 

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"X-API-ID": self.api_id, "X-API-KEY": self.api_key, "content-type":"application/json"}


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

    def format_xml(
        self,
        xml_item: Mapping[str, Any]
    ) -> str:
        # TODO: Find a way to remove hardcoded merchant
        merchant = "brmms"
        # xml_item["xml"]["nfeProc"]["NFe"]["infNFe"]["ide"]["dhEmi"],
        invoice = {
            "data": xml_item["xml"],
            "merchant": merchant.upper(),
            "source": "BR_ARQUIVEI",
            "type": f"{merchant}_notafiscal",
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

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):
        response = response.json()
        invoices = []

        for item in response['data']:

            item["xml"] = base64.b64decode(item["xml"])            
            xml_to_dict = xmltodict.parse(item["xml"])
            item["xml"] = xml_to_dict

            invoice = self.format_xml(item)
            invoices.append(invoice)

        # print(invoices)
        # with open('./converted.json', 'r+') as f:
        #     json.dump(response, f)
        #     f.truncate()
        return invoices


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
                return False, resp.json().get("error").get("code")
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # NoAuth just means there is no authentication required for this API. It's only included for completeness
        # of the example, but if you don't need authentication, you don't need to pass an authenticator at all.
        # Other authenticators are available for API token-based auth and Oauth2.
        auth = NoAuth()

        # Parse the date from a string into a datetime object
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")

        return [
            NfeReceived(authenticator=auth, config=config, start_date=start_date),
            NfeEmitted(authenticator=auth, config=config, start_date=start_date),
            Events(authenticator=auth, config=config, start_date=start_date)
        ]


    # def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
    #     # This method is called once for each record returned from the API to compare the cursor field value in that record with the current state
    #     # we then return an updated state object. If this is the first time we run a sync or no state was passed, current_stream_state will be None.
    #     if current_stream_state is not None and "date" in current_stream_state:
    #         current_parsed_date = datetime.strptime(current_stream_state["date"], "%Y-%m-%d")
    #         latest_record_date = datetime.strptime(latest_record["date"], "%Y-%m-%d")
    #         return {"date": max(current_parsed_date, latest_record_date).strftime("%Y-%m-%d")}
    #     else:
    #         return {"date": self.start_date.strftime("%Y-%m-%d")}

    # def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, any]]:
    #     """
    #     Returns a list of each day between the start date and now.
    #     The return value is a list of dicts {'date': date_string}.
    #     """
    #     dates = []
    #     while start_date < datetime.now():
    #         self.logger.info(start_date.strftime("%Y-%m-%d"))
    #         dates.append({"date": start_date.strftime("%Y-%m-%d")})
    #         start_date += timedelta(days=1)

    #     return dates

    # def stream_slices(
    #     self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    # ) -> Iterable[Optional[Mapping[str, any]]]:
    #     start_date = datetime.strptime(stream_state["date"], "%Y-%m-%d") if stream_state and "date" in stream_state else self.start_date
    #     return self._chunk_date_range(start_date)


# class SourceArquivei(AbstractSource):
#     def check_connection(self, logger, config) -> Tuple[bool, any]:
#         try:
            
#             headers = {
#                 "X-API-ID": config["api_id"],
#                 "X-API-KEY": config["api_key"],
#                 "content-type":"application/json"
#             }

#             result = requests.get('https://api.arquivei.com.br/v1/nfe/received', headers=headers)
#             print(result)
#             status = result.status_code
#             logger.info(f"Ping response code: {status}")
#             if status == 200:
#                 return True, None
#             else:
#                 return False, resp.json().get("error").get("code")
#         except Exception as e:
#             return False, e

#     def streams(self, config: Mapping[str, Any]) -> List[Stream]:
#         # NoAuth just means there is no authentication required for this API. It's only included for completeness
#         # of the example, but if you don't need authentication, you don't need to pass an authenticator at all.
#         # Other authenticators are available for API token-based auth and Oauth2.
#         auth = NoAuth()

#         # Parse the date from a string into a datetime object
#         start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")

#         # args = {
#         #     "X-API-ID":"d25100f602c9a5ef5e01bf4a9202ddeffcfe50d8",
#         #     "X-API-KEY":"f4a7cbd0976b7ccc1d11ec0768e3b343f7f42b1e",
#         #     "content-type":"application/json",
#         #     "start_date":start_date,
#         #     "config":config
#         # }
        
#         # return [NfeReceived(**args)]
#         return [NfeReceived(authenticator=auth, config=config, start_date=start_date)]
