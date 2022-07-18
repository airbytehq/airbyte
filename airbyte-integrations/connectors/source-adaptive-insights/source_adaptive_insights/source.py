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
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from source_adaptive_insights.serializers import (
    handle_export_dimensions,
    handle_export_levels
)


# Basic full refresh stream
class AdaptiveInsightsStream(HttpStream, ABC):

    url_base = "https://api.adaptiveinsights.com/api/"
    method = None

    def __init__(self, username: str, password: str, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.password = password

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    def request_headers(self, **kwargs) -> Mapping[str, Any]:

        return {'Content-Type': 'text/xml; charset=UTF-8'}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = xmltodict.parse(response.content)
        
        yield from handle_export_dimensions(json_response)


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
        args = {
            "username": username,
            "password": password
        }

        return [
            ExportDimensions(**args),
            ExportLevels(**args)
            # Employees(authenticator=auth)
        ]
