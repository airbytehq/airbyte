#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


# import logging
# logging.basicConfig(level=logging.DEBUG)

from abc import ABC
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Tuple, Optional
import pendulum

import requests
import json

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http import HttpStream

from .zuora_auth import ZuoraAuthenticator
from .zuora_errors import ZOQLQueryCannotProcessObject, ZOQLQueryFieldCannotResolve, ZOQLQueryFailed


def get_url_base(is_sandbox: bool = False) -> str:
    url_base = "https://rest.zuora.com"
    if is_sandbox:
        url_base = "https://rest.apisandbox.zuora.com"
    return url_base

class ZuoraStream(HttpStream, ABC):

    # Define primary key
    primary_key = "id"

    def __init__(self, config: Dict):
        super().__init__(authenticator=config["authenticator"])
        self.logger = AirbyteLogger()
        self._url_base = config["url_base"]
        self.start_date = config["start_date"]
        self.window_in_days = config["window_in_days"]
        self._config = config

    @property
    def url_base(self) -> str:
        return self._url_base

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def _request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return {"compression": "NONE", "output": {"target": "S3"}, "outputFormat": "JSON"}

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return {}

    def get_stream_state(self, stream_state: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return stream_state.get(self.cursor_field, stream_state.get(self.alt_cursor_field)) if stream_state else self.api.start_date
    
class ZuoraBase(ZuoraStream):

    def path(self, **kwargs) -> str:
        return ""

    def request_kwargs(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> Mapping[str, Any]:
        return stream_slice if stream_slice else {}
        

    def get_data(self, date_slice: Dict, config: Dict) -> Iterable[Mapping[str, Any]]:
        """
        This is the wrapper for 'Submit > Check > Get' operation.

        :: job_id - string with submited job_id EXAMPLE: '5a96ee43-e874-4a25-a9b4-004b39fe82a4'
            for more information see: ZuoraSubmitJob
        :: job_data_url - response object with:
                - 'queryStatus': ["completed", "in_progress", "failed", "canceled", "aborted"],
                - 'errorMessage': if there in any error on the server side during job execution
                - 'dataFile': if the execution was succesfull returns URL for jsonl file
            for more information see: ZuoraJobStatusCheck
        :: ZuoraGetJobResult - reads the 'dataFile' URL and outputs the data records for completed job
            for more information see: ZuoraGetJobResult

        """
        
        job_id: List[str] = ZuoraSubmitJob(self.query(date_slice=date_slice), config).read_records(sync_mode=None)
        job_data_url: List = ZuoraJobStatusCheck(list(job_id)[0], config).read_records(sync_mode=None)
        yield from ZuoraGetJobResult(list(job_data_url)[0], config).read_records(sync_mode=None)

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response: 
        try:
            yield from self.get_data(date_slice=request_kwargs, config=self._config)
        except ZOQLQueryFieldCannotResolve:
            """
            The default cursor_field is "updateddate" sometimes it's not supported by certain streams.
            We need to swith the default cursor field to alternative one, and retry again the whole operation, submit the new job to the server.
            We also need to save the state in the end of the sync. 
            So this switch is needed as fast and easy way of resolving the cursor_field for streams that support only the "createddate"
            """
            self.cursor_field = self.alt_cursor_field # cursor_field switch
            yield from self.get_data(date_slice=request_kwargs, config=self._config) # retry the whole operation
        except ZOQLQueryCannotProcessObject:
            pass
    
    def parse_response(self, response: requests.Response, **kwargs) -> str:
        yield from response

class ZuoraObjectsBase(ZuoraBase):

    cursor_field = "updateddate"
    alt_cursor_field = "createddate"

    # setting checkpoint interval to the limit of date-slice
    @property
    def state_checkpoint_interval(self) -> int: 
        return self.window_in_days

    def get_cursor_from_schema(self, schema: Dict) -> str:
        """
        Get the cursor_field from the stream's schema rather that take it from the class attribute
        If the stream doesn't support 'updateddate', then we use 'createddate'.
        """
        return self.cursor_field if self.cursor_field in schema else self.alt_cursor_field

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = list(ZuoraDescribeObject(self.name, config = self._config).read_records(sync_mode=None))
        return {"properties": {key: d[key] for d in schema for key in d} }

    def as_airbyte_stream(self) -> AirbyteStream:
        stream = super().as_airbyte_stream()
        stream.default_cursor_field = [self.get_cursor_from_schema(stream.json_schema["properties"])]
        return stream

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def query(self, date_slice: Dict) -> str:
        return f"""
            select * from {self.name} where 
            {self.cursor_field} >= TIMESTAMP '{date_slice.get('start_date')}' and 
            {self.cursor_field} <= TIMESTAMP '{date_slice.get('end_date')}'
            """

    @staticmethod
    def to_datetime_str(date: datetime) -> str:
        """
        :: Output example: '2021-07-15 07:45:55 -07:00' FROMAT : "%Y-%m-%d %H:%M:%S %Z"
        """
        return f"{date.strftime('%Y-%m-%d %H:%M:%S %Z')}"

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
    
        start_date = pendulum.parse(self.start_date).astimezone()
        end_date = pendulum.now().astimezone()

        # Determine stream_state, if no stream_state we use start_date
        if stream_state:
            start_date = pendulum.parse(stream_state.get(self.cursor_field, stream_state.get(self.alt_cursor_field)))

        # use the lowest date between start_date and self.end_date, otherwise API fails if start_date is in future
        start_date = min(start_date, end_date)
        date_slices = []

        while start_date < end_date:
            end_date_slice = start_date.add(days=self.window_in_days)
            date_slices.append(
                {
                    "start_date": self.to_datetime_str(start_date),
                    "end_date": self.to_datetime_str(end_date_slice)
                }
            )
            start_date = end_date_slice

        return date_slices
   
class ZuoraListObjects(ZuoraBase):

    def query(self, **kwargs) -> str:
        return "SHOW TABLES"
    
    def path(self, **kwargs) -> str:
        return ""

    def parse_response(self,response: requests.Response,**kwargs) -> Iterable[Mapping]:
        self.logger.info("Retrieving the list of available Objects from Zuora")
        return [name["Table"] for name in response]

class ZuoraDescribeObject(ZuoraBase):

    def __init__(self, zuora_object_name: str, config: Dict):
        super().__init__(config)
        self.zuora_object_name = zuora_object_name
 
    def query(self, **kwargs) -> str:
        self.logger.info(f"Getting schema information for {self.zuora_object_name}")
        return f"DESCRIBE {self.zuora_object_name}"

    def parse_response(self, response: requests.Response, **kwargs) -> List[Dict]:
        """ 
        Response example:
        [
            {'Column': 'taxexempteffectivedate', 'Type': 'date', 'Extra': '', 'Comment': 'TaxExemptEffectiveDate'}, 
            {'Column': 'invoicetemplateid', 'Type': 'varchar', 'Extra': '', 'Comment': 'InvoiceTemplateId'}...
        ]
        """
        type_number = ["number", "null"]
        type_string = ["string", "null"]
        type_object = ["object", "null"]
        type_array = ["array", "null"]
        type_bool = ["boolean", "null"]

        type_mapping = {
            "decimal(22,9)": type_number,
            "integer": type_number,
            "int": type_number,
            "bigint": type_number,
            "smallint": type_number,
            "timestamp": type_number,
            "date": type_string,
            "datetime": type_string,
            "timestamp with time zone": type_string,
            "picklist": type_string,
            "text": type_string,
            "varchar": type_string,
            "zoql": type_object,
            "binary": type_object,
            "json": type_object,
            "xml": type_object,
            "blob": type_object,
            "list": type_array, 
            "array": type_array,
            "boolean": type_bool,
            "bool": type_bool
            }

        json_schema = {}
        for field in response:
            json_type = type_mapping.get(field.get("Type"), type_string)
            json_schema[field.get("Column")] = {"type": json_type}

        return [json_schema]

class ZuoraSubmitJob(ZuoraStream):

    http_method = "POST"

    def __init__(self, query: str, config: Dict):
        super().__init__(config)
        self.query = query

    def path(self, **kwargs) -> str:
        return "/query/jobs"

    def request_body_json(self,**kwargs) -> Optional[Mapping]:
        params = self._request_params(stream_state=None)
        params["query"] = self.query
        return params

    def parse_response(self,response: requests.Response,**kwargs) -> List[str]:

        """ 
        Response example:
        {'data': 
            {
                'id': 'c6f25f91-5357-4fec-a00d-9009cc1ae856', 
                'query': 'DESCRIBE account', 
                'useIndexJoin': False, 
                'sourceData': 'LIVE', 
                'queryStatus': 'accepted', 
                'remainingRetries': 3, 
                'retries': 3, 
                'updatedOn': '2021-07-26T15:33:48.287Z', 
                'createdBy': '84f78cea-8a5b-4332-933f-27439fe3b87b'
            }
        }
        """
        return [ response.json()["data"]["id"] ]

class ZuoraJobStatusCheck(ZuoraStream):

    def __init__(self, job_id: str, config: Dict):
        super().__init__(config)
        self.job_id = job_id

    def path(self, **kwargs) -> str:
        return f"/query/jobs/{self.job_id}"

    def parse_response(self, response: requests.Response, **kwargs) -> List[str]:
       return [response.json()["data"]["dataFile"]]

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:

        """ 
        {'data': 
            {
                'id': 'c6f25f91-5357-4fec-a00d-9009cc1ae856', 
                'query': 'DESCRIBE account', 
                'useIndexJoin': False, 
                'sourceData': 'LIVE', 
                'queryStatus': 'completed', 
                'dataFile': 'https://owl-auw2-sbx01-query-result.s3.us-west-2.amazonaws.com/c6f25f91-5357-4fec-a00d-9009cc1ae856_2779514650704989.jsonl?....', 
                'outputRows': 53, 
                'processingTime': 516, 
                'remainingRetries': 3, 
                'retries': 3, 
                'updatedOn': '2021-07-26T15:33:48.803Z', 
                'createdBy': '84f78cea-8a5b-4332-933f-27439fe3b87b'
            }
        }
        """

        # Define the job error statuses
        errors = ["failed", "canceled", "aborted"]
        # Error msg: the cursor_field cannot be resolved
        cursor_error = "Column 'updateddate' cannot be resolved"
        # Error msg: cannot process object
        obj_read_error = "failed to process object"

        status = None
        success = "completed"
        while status != success:
            response: requests.Response = self._session.send(request, **request_kwargs)
            job_check = response.json()
            status = job_check["data"]["queryStatus"]
            if status in errors and cursor_error in job_check["data"]["errorMessage"]:
                raise ZOQLQueryFieldCannotResolve
            elif status in errors and obj_read_error in job_check["data"]["errorMessage"]:
                raise ZOQLQueryCannotProcessObject
            elif status in errors:
                raise ZOQLQueryFailed(response)
        return response
 
class ZuoraGetJobResult(HttpStream):

    # TODO: describe the dataFile is comming from...from S3
    primary_key = None

    def __init__(self, url: str, config: Dict):
        super().__init__()
        self.url = url

    @property
    def url_base(self):
        return self.url

    def path(self, **kwargs) -> str:
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> str:
        yield from [json.loads(line) for line in response.text.splitlines()]

class SourceZuora(AbstractSource):

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector by granting the token.
        """

        # Define the endpoint from user's config
        url_base = get_url_base(config['is_sandbox'])
        try:
            ZuoraAuthenticator(
                token_refresh_endpoint = f"{url_base}/oauth/token",
                client_id = config["client_id"],
                client_secret = config["client_secret"], 
                refresh_token = None, # Zuora doesn't have Refresh Token parameter.
            ).get_auth_header()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[ZuoraStream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Defining streams to run by building stream classes dynamically.
        """
        # Define the endpoint from user's config
        url_base = get_url_base(config['is_sandbox'])

        # Get Authotization Header with Access Token
        authenticator = ZuoraAuthenticator(
            token_refresh_endpoint = f"{url_base}/oauth/token",
            client_id = config["client_id"],
            client_secret = config["client_secret"], 
            refresh_token = None, # Zuora doesn't have Refresh Token parameter.
        )

        config["authenticator"] = authenticator
        config["url_base"] = url_base

         # List available objects (streams) names from Zuora
        # zuora_stream_names = ["account", "invoicehistory", "ratedusage"]
        zuora_stream_names = ZuoraListObjects(config).read_records(sync_mode=None)

        streams: List[ZuoraStream] = []
        for stream_name in zuora_stream_names:
            # construct ZuoraReadStreams sub-class for each stream_name
            stream_class = type(stream_name, (ZuoraObjectsBase,), {"cursor_field": "updateddate"})
            # instancetiate a stream with config
            stream_instance = stream_class(config)
            streams.append(stream_instance)
        
        return streams

