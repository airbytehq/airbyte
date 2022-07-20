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
from uuid import uuid4


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
        # file_path = os.path.join(os.getcwd(), f"{str(uuid4())}.xml")
        url = f"{self.url_base}v32"

        return requests.post(
            url,
            data=xml_body,
            headers=self.request_headers()
        )

        # with requests.post(
        #     self.url_base,
        #     data=xml_body,
        #     headers=self.request_headers(),
        #     stream=True
        # ) as r:

        #     r.raise_for_status()
        #     with open(file_path, 'wb') as fp:
        #         for chunk in r.iter_content(chunk_size=1024000): 
        #             fp.write(chunk)
            
        #     return file_path


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
        
        yield from handle_export_dimensions(json_response)


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
        
        yield from handle_export_levels(json_response)


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
        
        yield from handle_export_accounts(json_response)


class ExportData(AdaptiveInsightsStream):

    primary_key = "id"
    http_method = "POST"
    method = "exportData"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "v32"

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

        body = f"""<?xml version='1.0' encoding='UTF-8'?>
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

        holder = """
        """

        return body

    # def request_body_data(
    #     self,
    #     stream_state: Mapping[str, Any],
    #     stream_slice: Mapping[str, Any] = None,
    #     next_page_token: Mapping[str, Any] = None,
    # ) -> Optional[Union[Mapping, str]]:

    #     body = f"""<?xml version='1.0' encoding='UTF-8'?>
    #     <call method="{self.method}" callerName="Airbyte - auto">
    #     <credentials login="{self.username}" password="{self.password}"/>
    #     <version name="LBE0722" isDefault="false"/>
    #     <format useInternalCodes="true" includeCodes="false" includeNames="true" displayNameEnabled="true"/>
    #     <filters>
    #     <timeSpan start="01/2021" end="02/2021"/>
    #     </filters>
    #     <dimensions>
    #     <dimension name="GL Account"/>
    #     <dimension name="Assignment"/>
    #     <dimension name="Location" />
    #     <dimension name="Contract"/>
    #     <dimension name="Assets"/>
    #     </dimensions>
    #     <rules includeZeroRows="false" includeRollupAccounts="true" timeRollups="true">
    #     <currency override="USD"/>
    #     </rules>
    #     </call>
    #     """.encode("utf-8")

        return body

    @staticmethod
    def add_one_month(date_str: str) -> str:
        date_obj = datetime.strptime(date_str, "%m/%Y")
        year = date_obj.year
        month = date_obj.month

        if month == 12:
            month == 1
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
        current_date = datetime.now().strftime("%m/%Y")

        start_date = self.start_date

        while True:
            
            self.logger.info(f"Runing `export_data` for period {start_date} for version {self.version_type} with argument: start_date {self.start_date}")
            response = self.send_data_request(xml_body=self.construct_xml_body(start_date=start_date, end_date=start_date))
            
            for record in self.parse_response(response):
                yield record

            if current_date == start_date:
                break

            start_date = self.add_one_month(start_date)

        yield from []

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        json_response = xmltodict.parse(response.content)
        
        yield from handle_export_data(json_response)


# Basic incremental stream
# class IncrementalAdaptiveInsightsStream(AdaptiveInsightsStream, ABC):
#     """
#     TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
#          if you do not need to implement incremental sync for any streams, remove this class.
#     """

#     # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
#     state_checkpoint_interval = None

#     @property
#     def cursor_field(self) -> str:
#         """
#         TODO
#         Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
#         usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

#         :return str: The name of the cursor field.
#         """
#         return []

#     def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
#         """
#         Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
#         the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
#         """
#         return {}


# class Employees(IncrementalAdaptiveInsightsStream):
#     """
#     TODO: Change class name to match the table/data source this stream corresponds to.
#     """

#     # TODO: Fill in the cursor_field. Required.
#     cursor_field = "start_date"

#     # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
#     primary_key = "employee_id"

#     def path(self, **kwargs) -> str:
#         """
#         TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
#         return "single". Required.
#         """
#         return "employees"

#     def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
#         """
#         TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

#         Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
#         This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
#         section of the docs for more information.

#         The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
#         necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
#         This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

#         An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
#         craft that specific request.

#         For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
#         this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
#         till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
#         the date query param.
#         """
#         raise NotImplementedError("Implement stream slices or delete this method!")


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
            ExportData(**args)
            # Employees(authenticator=auth)
        ]
