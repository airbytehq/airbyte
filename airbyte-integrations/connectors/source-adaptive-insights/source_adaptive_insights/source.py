#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import (
    Any,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union
)
import requests
import xmltodict
import os
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from source_adaptive_insights.serializers import (
    handle_export_dimensions,
    handle_export_levels,
    handle_export_accounts,
    handle_export_data
)
from datetime import datetime


# Basic full refresh stream
class AdaptiveInsightsStream(HttpStream, ABC):

    url_base = "https://api.adaptiveinsights.com/api/"
    method = None

    def __init__(self, username: str, password: str, version_type: str, start_date: str, accounts: str, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.password = password
        self.version_type = version_type
        self.start_date = start_date
        self.accounts = accounts

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    def request_headers(self, **kwargs) -> Mapping[str, Any]:

        return {'Content-Type': 'text/xml; charset=UTF-8'}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        pass

    def send_data_request(self, xml_body: str) -> str:
        url = f"{self.url_base}v32"

        return requests.post(
            url,
            data=xml_body,
            headers=self.request_headers()
        )


class ExportDimensions(AdaptiveInsightsStream):

    primary_key = "id"
    http_method = "POST"
    method = "exportDimensions"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "v32"

    def request_body_data(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:

        body = f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{self.method}" callerName="Airbyte - auto">
        <credentials login="{self.username}" password="{self.password}"/>
        <include versionName="Current LBE" dimensionValues="true"/>
        </call>
        """.encode("utf-8")

        return body

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = xmltodict.parse(response.content)
        
        yield from handle_export_dimensions(data=json_response, version=self.version_type)


class ExportLevels(AdaptiveInsightsStream):

    primary_key = "id"
    http_method = "POST"
    method = "exportLevels"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "v32"

    def request_body_data(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:

        body = f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{self.method}" callerName="Airbyte - auto">
        <credentials login="{self.username}" password="{self.password}"/>
        <include versionName="Current LBE" inaccessibleValues="true"/>
        </call>
        """.encode("utf-8")

        return body

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = xmltodict.parse(response.content)
        
        yield from handle_export_levels(d=json_response, version=self.version_type)


class ExportAccounts(AdaptiveInsightsStream):

    primary_key = "id"
    http_method = "POST"
    method = "exportAccounts"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "v32"

    def request_body_data(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Union[Mapping, str]]:

        body = f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{self.method}" callerName="Airbyte - auto">
        <credentials login="{self.username}" password="{self.password}"/>
        <include versionName="Current LBE" inaccessibleValues="true"/>
        </call>
        """.encode("utf-8")

        return body

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = xmltodict.parse(response.content)
        
        yield from handle_export_accounts(d=json_response, version=self.version_type)


class ExportData(AdaptiveInsightsStream):

    primary_key = "id"
    http_method = "POST"
    method = "exportData"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "v32"

    @property
    def limit(self) -> int:
        return 1000

    state_checkpoint_interval = limit

    def construct_account_payload(self) -> str:
        if not self.accounts:
            return ""
        list_of_accounts = self.accounts.split(',')
        payload = "<accounts>"
        for account in list_of_accounts:
            payload += f"<account code=\"{account}\" isAssumption=\"false\" includeDescendants=\"true\"/>"
        payload += "</accounts>"

        return payload


    def construct_xml_body(self, start_date: str, end_date: str) -> str:

        return f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{self.method}" callerName="Airbyte - auto">
        <credentials login="{self.username}" password="{self.password}"/>
        <version name="{self.version_type}" isDefault="false"/>
        <format useInternalCodes="true" includeCodes="false" includeNames="true" displayNameEnabled="true"/>
        <filters>
        {self.construct_account_payload()}
        <timeSpan start="{start_date}" end="{end_date}"/>
        </filters>
        <dimensions>
        <dimension name="GL Account"/>
        <dimension name="Location" />
        <dimension name="Contract"/>
        <dimension name="Assignment"/>
        </dimensions>
        <rules includeZeroRows="false" includeRollupAccounts="true" timeRollups="false">
        <currency override="USD"/>
        </rules>
        </call>
        """.encode("utf-8")


    @staticmethod
    def add_one_month(date_str: str) -> str:
        date_obj = datetime.strptime(date_str, "%m/%Y")
        year = date_obj.year
        month = date_obj.month

        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        
        return f"{str(month).zfill(2)}/{year}"

    def read_records(
        self,
        sync_mode: SyncMode,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False
        current_year = datetime.now().year
        end_date = f"{current_year}-12"
        start_date = self.start_date

        while True:
            
            self.logger.info(f"Runing `export_data` for period {start_date} for version {self.version_type} with argument `start_date:{self.start_date}` - `end_date:{end_date}`")
            response = self.send_data_request(xml_body=self.construct_xml_body(start_date=start_date, end_date=start_date))
            
            for record in self.parse_response(response):
                yield record

            if datetime.strptime(start_date, "%m/%Y") >= datetime.strptime(end_date, "%Y-%m"):
                break

            start_date = self.add_one_month(start_date)

        yield from []

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        json_response = xmltodict.parse(response.content)
        
        yield from handle_export_data(response=json_response, version=self.version_type)


class ExportHeadCount(AdaptiveInsightsStream):

    primary_key = "id"
    http_method = "POST"
    method = "exportData"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "v32"

    @property
    def limit(self) -> int:
        return 1000

    state_checkpoint_interval = limit

    def construct_account_payload(self) -> str:
        if not self.accounts:
            return ""
        list_of_accounts = self.accounts.split(',')
        payload = "<accounts>"
        for account in list_of_accounts:
            payload += f"<account code=\"{account}\" isAssumption=\"false\" includeDescendants=\"true\"/>"
        payload += "</accounts>"

        return payload


    def construct_xml_body(self, start_date: str, end_date: str) -> str:

        return f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{self.method}" callerName="Airbyte - auto">
        <credentials login="{self.username}" password="{self.password}"/>
        <version name="{self.version_type}" isDefault="false"/>
        <format useInternalCodes="true" includeCodes="false" includeNames="true" displayNameEnabled="true"/>
        <filters>
        {self.construct_account_payload()}
        <timeSpan start="{start_date}" end="{end_date}"/>
        </filters>
        <dimensions>
        <dimension name="Position"/>
        <dimension name="Assignment" />
        <dimension name="Location"/>
        <dimension name="Personnel_Input_Type"/>
        </dimensions>
        <rules includeZeroRows="false" includeRollupAccounts="true" timeRollups="false">
        <currency useCorporate="false" useLocal="false" override="EUR"/>
        </rules>
        </call>
        """.encode("utf-8")


    @staticmethod
    def add_one_month(date_str: str) -> str:
        date_obj = datetime.strptime(date_str, "%m/%Y")
        year = date_obj.year
        month = date_obj.month

        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        
        return f"{str(month).zfill(2)}/{year}"

    def read_records(
        self,
        sync_mode: SyncMode,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False
        current_year = datetime.now().year
        end_date = f"{current_year}-12"
        start_date = self.start_date

        while True:
            
            self.logger.info(f"Runing `export_headcount` for period {start_date} for version {self.version_type} with argument `start_date:{self.start_date}` - `end_date:{end_date}`")
            response = self.send_data_request(xml_body=self.construct_xml_body(start_date=start_date, end_date=start_date))
            
            for record in self.parse_response(response):
                yield record

            if datetime.strptime(start_date, "%m/%Y") >= datetime.strptime(end_date, "%Y-%m"):
                break

            start_date = self.add_one_month(start_date)

        yield from []

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        json_response = xmltodict.parse(response.content)
        
        yield from handle_export_data(response=json_response, version=self.version_type)



# Source
class SourceAdaptiveInsights(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        username = config["username"]
        password = config["password"]

        BASE_URL = "https://api.adaptiveinsights.com/api/v32"

        headers = {'Content-Type': 'text/xml; charset=UTF-8'}

        xml_string = f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="exportDimensions" callerName="Airbyte - check">
        <credentials login="{username}" password="{password}"/>
        <include versionName="Current LBE" dimensionValues="true"/>
        </call>
        """.encode("utf-8")

        response = requests.post(
            BASE_URL,
            data=xml_string,
            headers=headers
        )

        content = xmltodict.parse(response.content)

        return content.get("response").get("@success") == 'true', None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        username = config["username"]
        password = config["password"]
        # dimensions = config["dimensions"]
        version_type = config["versionType"]
        start_date = config["startDate"]
        accounts = config["accounts"]

        args = {
            "username": username,
            "password": password,
            "version_type": version_type,
            "start_date": start_date,
            "accounts": accounts
        }

        return [
            ExportDimensions(**args),
            ExportLevels(**args),
            ExportAccounts(**args),
            ExportData(**args),
            ExportHeadCount(**args)
        ]
