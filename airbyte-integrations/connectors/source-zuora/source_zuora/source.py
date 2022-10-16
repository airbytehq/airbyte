#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from abc import ABC
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteStream, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http import HttpStream

from .zuora_auth import ZuoraAuthenticator
from .zuora_errors import (
    QueryWindowError,
    ZOQLQueryCannotProcessObject,
    ZOQLQueryFailed,
    ZOQLQueryFieldCannotResolveAltCursor,
    ZOQLQueryFieldCannotResolveCursor,
)
from .zuora_excluded_streams import ZUORA_EXCLUDED_STREAMS


class ZuoraStream(HttpStream, ABC):
    """
    Parent class for all other classes, except of SourceZuora.
    """

    # Define primary key
    primary_key = "id"

    # Define possible cursor_fields
    cursor_field = "updateddate"
    alt_cursor_field = "createddate"

    def __init__(self, config: Dict):
        super().__init__(authenticator=config["authenticator"])
        self._config = config

    @property
    def url_base(self) -> str:
        return self._config["url_base"]

    @property
    def window_in_days(self) -> float:
        """
        Converting `Query Window` config parameter from string type into type float.
        """
        try:
            value = self._config["window_in_days"]
            return float(value)
        except ValueError:
            raise QueryWindowError(value)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Abstractmethod HTTPStream CDK dependency"""
        return None

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """Abstractmethod HTTPStream CDK dependency"""
        return {}

    def base_query_params(self) -> MutableMapping[str, Any]:
        """
        Returns base query parameters for default CDK request_json_body method
        """
        params = {"compression": "NONE", "output": {"target": "S3"}, "outputFormat": "JSON"}
        if self._config["data_query"] == "Unlimited":
            params["sourceData"] = "DATAHUB"
        return params


class ZuoraBase(ZuoraStream):
    """
    Base child class, provides main functionality for next classes:
        - ZuoraObjectsBase, ZuoraListObjects, ZuoraDescribeObject
    """

    def path(self, **kwargs) -> str:
        """Abstractmethod HTTPStream CDK dependency"""
        return ""

    def request_kwargs(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Mapping[str, Any]:
        """
        Override of default CDK method to return date_slices as stream_slices
        """
        return stream_slice if stream_slice else {}

    def get_zuora_data(self, date_slice: Dict, config: Dict, full_object: bool = False) -> Iterable[Mapping[str, Any]]:
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
        :: full_object - boolean, indicates whether to fetch the whole object without any filtering, default `False`

        """
        if full_object:
            # If the cursor is not available, we fetch whole object
            job_query = self.query(stream_name=self.name, full_object=True)
        else:
            # Default prepared job with Cursor
            job_query = self.query(stream_name=self.name, cursor_field=self.cursor_field, date_slice=date_slice)

        job_id: List[str] = ZuoraSubmitJob(job_query, config).read_records(sync_mode=None)
        job_data_url: List = ZuoraJobStatusCheck(list(job_id)[0], config).read_records(sync_mode=None)
        yield from ZuoraGetJobResult(list(job_data_url)[0]).read_records(sync_mode=None)

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        """
        Override for _send_request CDK method to send HTTP request to the Zuora API
        """
        try:
            # try to fetch with default cursor_field = UpdatedDate
            yield from self.get_zuora_data(date_slice=request_kwargs, config=self._config)
        except ZOQLQueryCannotProcessObject:
            # do nothing if we cannot resolve the object
            pass
        except ZOQLQueryFieldCannotResolveCursor:
            """
            The default cursor_field is "updateddate" sometimes it's not supported by certain streams.
            We need to swith the default cursor field to alternative one, and retry again the whole operation, submit the new job to the server.
            We also need to save the state in the end of the sync.
            So this switch is needed as fast and easy way of resolving the cursor_field for streams that support only the "createddate"
            """
            # cursor_field switch to alternative = CreatedDate
            self.cursor_field = self.alt_cursor_field
            try:
                """
                The alternative cursor_field is "createddate", it could be also not available for some custom objects.
                In this case, we fetch the whole object without any filtering.
                """
                # retry the whole operation with alternative cursor
                yield from self.get_zuora_data(date_slice=request_kwargs, config=self._config)
            except ZOQLQueryFieldCannotResolveAltCursor:
                # if we fail to use the alternative cursor - fetch the whole object
                # retry the whole operation
                yield from self.get_zuora_data(date_slice=request_kwargs, config=self._config, full_object=True)
            except ZOQLQueryCannotProcessObject:
                # do nothing if we cannot resolve the object
                pass

    def parse_response(self, response: requests.Response, **kwargs) -> str:
        yield from response


class ZuoraObjectsBase(ZuoraBase):
    """
    Main class for all the Zuora data streams (Zuora Object names),
    provides functionality for dynamically created classes as streams of data.
    """

    @property
    def state_checkpoint_interval(self) -> float:
        return self.window_in_days

    @staticmethod
    def to_datetime_str(date: datetime) -> str:
        """
        Custom method.
        Returns the formated datetime string in a way Zuora API endpoint recognises it as timestamp.
        :: Output example: '2021-07-15 07:45:55 -07:00' FROMAT : "%Y-%m-%d %H:%M:%S.%f %Z"
        """
        return date.strftime("%Y-%m-%d %H:%M:%S.%f %Z")

    def get_cursor_from_schema(self, schema: Dict) -> str:
        """
        Get the cursor_field from the stream's schema rather that take it from the class attribute
        If the stream doesn't support 'updateddate', then we use 'createddate'.
        If the stream doesn't support 'createddate', then stream is `full_refresh` only.
        """
        if self.cursor_field in schema:
            # when UpdatedDate is availalbe
            return self.cursor_field
        elif self.alt_cursor_field in schema:
            # when CreatedDate is availalbe
            return self.alt_cursor_field
        else:
            return None

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Override get_json_schema CDK method to retrieve the schema information for Zuora Object dynamicaly.
        """
        schema = list(ZuoraDescribeObject(self.name, config=self._config).read_records(sync_mode=None))
        return {"type": "object", "properties": {key: d[key] for d in schema for key in d}}

    def as_airbyte_stream(self) -> AirbyteStream:
        """
        Override as_airbyte_stream CDK method to replace default 'default_cursor_field' behaviour,
        :: We use the cursor_field defined inside schema instead of using class attribute by default.
        :: But we still need the default class attribute 'cursor_field' in order to CDK read_records works properly.
        """
        stream = super().as_airbyte_stream()
        stream_cursor = self.get_cursor_from_schema(stream.json_schema["properties"])
        if stream_cursor:
            stream.default_cursor_field = [stream_cursor]
        else:
            # When there is no cursor available in the stream, we do Full-Refresh only.
            stream.supported_sync_modes = [SyncMode.full_refresh]
            stream.source_defined_cursor = True  # default CDK for full-refresh
            stream.default_cursor_field = []  # default CDK for full-refresh
        return stream

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Update the state value, default CDK method.
        """
        updated_state = max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))
        return {self.cursor_field: updated_state} if updated_state else {}

    def query(self, stream_name: str, cursor_field: str = None, date_slice: Dict = None, full_object: bool = False) -> str:
        """
        Custom method. Returns the SQL-like query in a way Zuora API endpoint accepts the jobs.
        """
        if full_object:
            return f"""select * from {stream_name}"""

        return f"""
            select *
            from {stream_name} where
            {cursor_field} >= TIMESTAMP '{date_slice.get('start_date')}' and
            {cursor_field} <= TIMESTAMP '{date_slice.get('end_date')}'
            order by {cursor_field} asc
            """

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override default stream_slices CDK method to provide date_slices as page chunks for data fetch.
        Returns list of dict, example: {
            "start_date": "2020-01-01 00:00:00 -07:00",
            "end_date": "2021-12-31 00:00:00 -07:00"
            },
            ...
        """

        start_date = pendulum.parse(self._config["start_date"]).astimezone()
        end_date = pendulum.now().astimezone()

        # Determine stream_state, if no stream_state we use start_date
        if stream_state:
            state = stream_state.get(self.cursor_field, stream_state.get(self.alt_cursor_field))
            start_date = pendulum.parse(state) if state else self._config["start_date"]

        # use the lowest date between start_date and self.end_date, otherwise API fails if start_date is in future
        start_date = min(start_date, end_date)

        while start_date <= end_date:
            end_date_slice = start_date.add(days=self.window_in_days)
            yield {"start_date": self.to_datetime_str(start_date), "end_date": self.to_datetime_str(end_date_slice)}
            start_date = end_date_slice


class ZuoraListObjects(ZuoraBase):
    """
    Provides functionality to retrieve the list of Zuora Objects as list of object names.
    """

    def query(self, **kwargs) -> str:
        return "SHOW TABLES"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return [name["Table"] for name in response]


class ZuoraDescribeObject(ZuoraBase):
    """
    Provides functionality to retrive Zuora Object (stream) schema dynamicaly from the endpoint,
    convert it into JSONSchema types, for the connector's catalog.
    """

    def __init__(self, zuora_object_name: str, config: Dict):
        super().__init__(config)
        self.zuora_object_name = zuora_object_name

    def query(self, **kwargs) -> str:
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
            "decimal": type_number,
            "integer": type_number,
            "int": type_number,
            "bigint": type_number,
            "smallint": type_number,
            "double": type_number,
            "float": type_number,
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
            "bool": type_bool,
        }

        json_schema = {}
        for field in response:
            json_type = type_mapping.get(field.get("Type"), type_string)
            json_schema[field.get("Column")] = {"type": json_type}

        return [json_schema]


class ZuoraSubmitJob(ZuoraStream):
    """
    Provides functionality to submit ZOQL Data Query job on the server.
    Return job_id as comfirmation of the successfully submited job.
    """

    http_method = "POST"

    def __init__(self, query: str, config: Dict):
        super().__init__(config)
        self.query = query

    def path(self, **kwargs) -> str:
        return "/query/jobs"

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        """
        Override of default CDK method to return SQL-like query and use it in _send_request method.
        """
        params = self.base_query_params()
        params["query"] = self.query
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> List[str]:

        """
        Response example:
        {'data':
            {
                'id': 'c6f25f91-5357-4fec-a00d-9009cc1ae856',
                'query': 'DESCRIBE account', # This could be SELECT statement or DESCRIBE or SHOW {object}
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
        return [response.json()["data"]["id"]]


class ZuoraJobStatusCheck(ZuoraStream):
    """
    Provedes functionaluty to check the status of submited job on the server.
    :: There are ["completed", "in_progress", "failed", "canceled", "aborted"] statuses available in check response.
    The check operation returns either dataFile URL or error message describing the error.
    """

    def __init__(self, job_id: str, config: Dict):
        super().__init__(config)
        self.job_id = job_id

    def path(self, **kwargs) -> str:
        return f"/query/jobs/{self.job_id}"

    def parse_response(self, response: requests.Response, **kwargs) -> List[str]:
        return [response.json()["data"]["dataFile"]]

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:

        """
        Override of default CDK method _send_request to check the status of submited job iteratevely,
        until it's either "completed" or "failed" or "canceled" for any reason.

        Response example:
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
        cursor_error = f"Column '{self.cursor_field}' cannot be resolved"
        alt_cursor_error = f"Column '{self.alt_cursor_field}' cannot be resolved"
        # Error msg: cannot process object
        obj_read_error = "failed to process object"

        status = None
        success = "completed"
        while status != success:
            """
            There is no opportunity for the infinity loop because the operation performs on the server-side,
            there are query run-time limitations: if the query time is longer than 120 min,
            the server will output the error with the corresponding message for the user in the output,
            by raising `ZOQLQueryFailed` exception.
            """

            response: requests.Response = self._session.send(request, **request_kwargs)
            job_check = response.json()
            status = job_check["data"]["queryStatus"]
            if status in errors and cursor_error in job_check["data"]["errorMessage"]:
                raise ZOQLQueryFieldCannotResolveCursor
            elif status in errors and obj_read_error in job_check["data"]["errorMessage"]:
                raise ZOQLQueryCannotProcessObject
            elif status in errors and alt_cursor_error in job_check["data"]["errorMessage"]:
                raise ZOQLQueryFieldCannotResolveAltCursor
            elif status in errors:
                raise ZOQLQueryFailed(response)
        return response


class ZuoraGetJobResult(HttpStream):
    """
    Provides functionality to retrive the records from the file formed by submited and successfully completed job
    DataFile URL example:
        {'data':
                {
                    'id': 'c6f25f91-5357-4fec-a00d-9009cc1ae856',
                    ...,
                    ...,
                    'dataFile': 'https://owl-auw2-sbx01-query-result.s3.us-west-2.amazonaws.com/c6f25f91-5357-4fec-a00d-9009cc1ae856_2779514650704989.jsonl?....',
                    ...,
                    ...,
                    'createdBy': '84f78cea-8a5b-4332-933f-27439fe3b87b'
                }
        }
    """

    primary_key = None

    def __init__(self, url: str):
        super().__init__()  # initiate authenticator = NoAuth(), _session
        self.url = url  # accept incoming dataFile URL

    @property
    def url_base(self):
        return self.url

    def path(self, **kwargs) -> str:
        """Abstractmethod HTTPStream CDK dependency"""
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Abstractmethod HTTPStream CDK dependency"""
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> str:
        """
        Return records from JSONLines file from dataFile URL.
        """
        for line in response.text.splitlines():
            yield json.loads(line)


class SourceZuora(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector by granting the token.
        """
        auth = ZuoraAuthenticator(config).get_auth()
        try:
            auth.get_auth_header()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[ZuoraStream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Defining streams to run by building stream classes dynamically.
        """
        auth = ZuoraAuthenticator(config)
        config["authenticator"] = auth.get_auth()
        config["url_base"] = auth.url_base

        # List available objects (streams) names from Zuora
        # Example: zuora_stream_names = ["account", "country", "user"]
        zuora_stream_names = ZuoraListObjects(config).read_records(sync_mode=None)

        streams: List[ZuoraStream] = []
        for stream_name in zuora_stream_names:
            if stream_name not in ZUORA_EXCLUDED_STREAMS:
                # construct ZuoraReadStreams sub-class for each stream_name
                stream_class = type(stream_name, (ZuoraObjectsBase,), {})
                # instancetiate a stream with config
                stream_instance = stream_class(config)
                streams.append(stream_instance)
        return streams
