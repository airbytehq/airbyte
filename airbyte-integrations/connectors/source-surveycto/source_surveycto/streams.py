# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import base64
import csv
import io
import json
import re
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib import response

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from bigquery_schema_generator.generate_schema import SchemaGenerator
from gbqschema_converter.gbqschema_to_jsonschema import json_representation as converter

from .helpers import Helpers


class SurveyctoStream(HttpStream, ABC):
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.server_name = config["server_name"]
        self.form_id = config["form_id"]

        self.dataset_id = config["dataset_id"]
        # base64 encode username and password as auth token
        user_name_password = f"{config['username']}:{config['password']}"
        self.auth_token = Helpers._base64_encode(user_name_password)
        self.start_date = config["start_date"]
        self.username = config["username"]
        self.password = config["password"]
        self.auth_basic = requests.auth.HTTPBasicAuth(config["username"], config["password"])
        self._sesh = requests.session()
        self.key = config["key"]
        self._provider = config["media_files"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def url_base(self) -> str:
        return f"https://{self.server_name}.surveycto.com/"


# This class will handle all the form data from the survey
class FormData(SurveyctoStream, IncrementalMixin):
    """
    API docs: https://{server_name}.surveycto.com/api/v2/forms/data/wide/json/{form_id}?date={start_date}
    """

    primary_key = "KEY"
    cursor_field = "CompletionDate"
    _cursor_value = None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        ix = self.start_date
        return {"date": ix}

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        return {"Authorization": "Basic " + self.auth_token}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Returns the updated state for the stream based on the current stream state and the latest record.
        This is the completion date of the latest record.

        Args:
            current_stream_state (MutableMapping[str, Any]): The current state of the stream.
            latest_record (Mapping[str, Any]): The latest record to be processed.

        Returns:
            Mapping[str, Any]: The updated state for the stream.

        """
        if current_stream_state is None:
            state_ts = None
        else:
            if isinstance(current_stream_state.get(self.cursor_field), str):
                state_ts = pendulum.parse(current_stream_state.get(self.cursor_field, None), strict=False)
            else:
                state_ts = current_stream_state.get(self.cursor_field, None)
        if state_ts is None:
            return {self.cursor_field: pendulum.parse(latest_record[self.cursor_field], strict=False)}

        return {self.cursor_field: max(pendulum.parse(latest_record[self.cursor_field], strict=False), state_ts)}

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: pendulum.parse(self._cursor_value, strict=False)}
        else:
            return {self.cursor_field: pendulum.parse(self.start_date, strict=False)}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def get_json_schema(self):
        dynamic_schema = {}
        if self.form_id == "form_id":
            dynamic_schema = {
                "type": "object",
                "properties": {},
            }
        else:
            *_, last = self.read_records(SyncMode.incremental)
            dynamic_schema = Helpers.get_filter_data(last)
            return dynamic_schema

    def path(self, **kwargs) -> str:
        return f"api/v2/forms/data/wide/json/{self.form_id}"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        start_point = stream_state.get(self.cursor_field, None) if stream_state else None
        # Check if start point is None. The default start point is set on configs.
        if start_point is None:
            self.start_date = pendulum.parse(self.start_date, strict=False).isoformat()
            start_point = Helpers.format_date(self.start_date)
        else:
            start_point = pendulum.parse(start_point, strict=False).isoformat()
            start_point = Helpers.format_date(start_point)

        oldest_completion_date = start_point  # The data will be filtered based on the completion date

        url = f"{self.url_base}{self.path()}?date={oldest_completion_date}"
        records = Helpers.fetch_records(url, self.auth_basic, self.key, type="json")
        if records is None:
            return [{}]  # return empty record if no records are found
        else:
            for record in records:

                self._cursor_value = record[self.cursor_field]
                record[self.cursor_field] = pendulum.parse(record[self.cursor_field], strict=False).isoformat()

                yield from self.parse_response(
                    response=record,
                    stream_state=stream_state,
                    stream_slice=stream_slice,
                )

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        return [response]


# This class will handle getting data from a dataset
class FormDataset(SurveyctoStream):
    """
    API docs: https://{self.server_name}.surveycto.com/api/v2/datasets/data/csv/{dataset_id}
    """

    primary_key = ""

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        return {"Authorization": "Basic " + self.auth_token}

    def get_json_schema(self):
        dynamic_schema = {}
        if self.dataset_id == "dataset_id":
            dynamic_schema = {
                "type": "object",
                "properties": {},
            }
        else:
            *_, last = self.read_records(SyncMode.incremental)

            dynamic_schema = Helpers.get_filter_data(last)
        return dynamic_schema

    def path(self, **kwargs) -> str:
        return f"api/v2/datasets/data/csv/{self.dataset_id}"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        server_name = self.server_name

        url = self.url_base + self.path()

        for record in Helpers.fetch_records(url, self.auth_basic, self.key, type="csv"):
            yield record

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        return


# This class will handle getting urls of the media files and downloading them.
# The assumption is that the urls have been extracted from the SurveyCTO using the FormData stream and they have been processed and stored in a file.
# The file should have a column with the urls and another column with the file names.
class Mediafiles(SurveyctoStream):
    """
    Represents a stream for retrieving media files from SurveyCTO.

    This stream is responsible for fetching media files from SurveyCTO,
    It provides methods for retrieving the URLs of the media files,
    reading the records from the URLs, and getting the JSON schema for the stream.

    Attributes:
        primary_key (str): The primary key of the stream.

    Methods:
        path(**kwargs) -> str: Returns the path of the stream.
        parse_response() -> List: Parses the response from the stream.
        get_urls() -> List[str]: Retrieves the URLs of the media files.
        read_records(sync_mode, cursor_field, stream_slice, stream_state) -> Iterable[Mapping[str, Any]]:
            Reads the records from the media file URLs.
        get_json_schema() -> Dict[str, Any]: Retrieves the JSON schema for the stream.
    """

    primary_key = ""

    def path(self, **kwargs) -> str:
        return

    def parse_response(self):
        return []

    def get_urls(self):
        storage_name = self._provider["storage"].upper()

        if storage_name == "LOCAL":
            file_path = self._provider["file_path"]
            file_name = self._provider["file_name"]
            column = self._provider["url_column"]
            return Helpers._get_local_urls(file_path, file_name, column)
        elif storage_name == "S3":
            aws_access_key_id = self._provider["access_key_id"]
            aws_secret_access_key = self._provider["secret_access_key"]
            bucket_name = self._provider["bucket"]
            region_name = self._provider["region_name"]
            file_key = self._provider["file_key"]
            column = self._provider["url_column"]

            return Helpers._get_s3_urls(aws_access_key_id, aws_secret_access_key, bucket_name, region_name, file_key, column)
        else:
            raise Exception("Storage provider not recognized.")

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        urls = self.get_urls()

        for url in urls:
            retry_count = 0
            name = url.split("/")[-1].split(".")[0]

            while True:
                try:

                    auth_basic = self.auth_basic
                    default_headers = {
                        "X-OpenRosa-Version": "1.0",
                    }

                    # check if url is valid
                    url_pattern = re.compile(r"^(?:http|ftp)s?://")  # https:// or ftp
                    if url_pattern.match(url) is None:
                        raise Exception("Invalid URL")

                    if self.key == "key" or self.key == "":
                        full_record = ""  # The record will be base64 encoded string
                        with requests.get(url, headers=default_headers, auth=auth_basic, stream=True) as stream:
                            stream.raise_for_status()

                            full_record = base64.b64encode(stream.content).decode("utf-8")
                        yield {"data": full_record, "name": name, "file_type": stream.headers["Content-Type"]}
                    else:
                        files = {"private_key": self.key}
                        full_record = ""
                        with requests.post(url, files=files, auth=auth_basic, stream=True) as stream:
                            stream.raise_for_status()

                            full_record = base64.b64encode(stream.content)
                        yield {"data": full_record, "name": name, "file_type": stream.headers["Content-Type"]}

                    break
                except requests.exceptions.HTTPError as e:
                    if (e.response.status_code == 500) & (retry_count < 5):
                        retry_count = retry_count + 1
                    elif e.response.status_code == 500:
                        yield {"data": None, "name": name}
                    elif e.response.status_code == 400:
                        yield {"data": None, "name": name}
                    else:
                        raise e

    def get_json_schema(self):
        schema = {"type": "object", "properties": {"data": {"type": "string"}, "name": {"type": "string"}, "file_type": {"type": "string"}}}
        return schema


# This class will get all the metadata of the survey
class FormDefinitionData(SurveyctoStream):
    primary_key = ""
    """
    API docs: https://{server_name}.surveycto.com/forms/{self.form_id}/design
    """

    def __auth(self):
        """
        Establish CSRF token and login
        """

        url = self.url_base

        try:
            response = self._sesh.head(url)
            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise e

        headers = {"X-csrf-token": response.headers["X-csrf-token"]}

        auth = self._sesh.post(
            url + "login",
            cookies=self._sesh.cookies,
            headers=headers,
            auth=self.auth_basic,
        )

        headers["X-csrf-token"] = auth.headers["X-csrf-token"]

        return headers

    def get_json_schema(self):
        dynamic_schema = {}
        if self.form_id == "form_id":
            dynamic_schema = {"type": "object", "properties": {}}
        else:
            *_, last = self.read_records(SyncMode.incremental)
            if last is None:
                dynamic_schema = {"type": "object", "properties": {}}
            else:
                dynamic_schema = Helpers.get_filter_data(last)
            return dynamic_schema

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        headers = self.__auth()

        return headers

    def request_cookies(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        return self._sesh.cookies

    def path(self, **kwargs) -> str:
        url = self.url_base
        return f"{url}forms/{self.form_id}/design"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        return [response]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        headers = self.__auth()

        try:
            response = self._sesh.get(
                self.path(),
                cookies=self._sesh.cookies,
                headers=headers,
            )
            response.raise_for_status()
            response_json = response.json()

            settings = response_json["settingsRowsAndColumns"]
            choices = response_json["choicesRowsAndColumns"]
            questions = response_json["fieldsRowsAndColumns"]

            settings_json = dict(zip(settings[0], settings[1]))
            choices_json = dict(zip(choices[0], choices[1]))
            questions_json = dict(zip(questions[0], questions[1]))

            final_data = {
                "settings": settings_json,
                "choices": choices_json,
                "questions": questions_json,
            }

            yield from self.parse_response(
                response=final_data,
                stream_state=stream_state,
                stream_slice=stream_slice,
            )
        except requests.exceptions.HTTPError as e:
            print(e)
            raise e
        except Exception as e:
            print(e)
            raise e


# This class will handle extracting repeat groups data for a form id
class FormRepeatGroupData(SurveyctoStream):
    """
    The class extracts all repeat groups belonging to a form and returns a key value record of a repeat group name and it's corresponding data
    This stream is only applicable if the form has repeat groups configured
    """

    primary_key = ""

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        ix = self.start_date
        return {"date": ix}

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        return {"Authorization": "Basic " + self.auth_token}

    def path(self, **kwargs) -> str:
        return ""

    def get_json_schema(self):
        schema = {"type": "object", "properties": {"data": {"repeatGroup": "object"}}}
        return schema

    def get_repeat_groups(self):
        """
        Private function to get the dictionary with repeat group {name: url} pairs

        """
        try:
            encryption_key = self.key or None

            files_url = f"""https://{self.server_name}.surveycto.com/api/v1/forms/files/csv/{self.form_id}"""
            base_url = f"""https://{self.server_name}.surveycto.com/api/v1/forms/data/csv/{self.form_id}"""
            if encryption_key is None:
                response = self._sesh.get(files_url, auth=self.auth_basic)
            else:
                key_config = {"private_key": encryption_key}
                response = self._sesh.post(
                    files_url,
                    files=key_config,
                    # auth=self.auth_token
                    auth=self.auth_basic,
                )
            url_list = response.text
            repeat_groups_dict = {}
            for url_count, url in enumerate(url_list.splitlines()):
                if url_count > 0:
                    repeat_group_name = url.replace(base_url + "/", "")
                    repeat_groups_dict[repeat_group_name] = url

            return repeat_groups_dict

        except Exception as e:
            # Log the exception
            self.logger.exception(f"An error occurred in get_repeat_groups function: {str(e)}")
            # Raise the exception to stop the execution
            raise e

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        # self.response_json = response.json()
        return [response]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        try:
            repeat_groups_dict = self.get_repeat_groups()

            if len(repeat_groups_dict.keys()) == 0:
                raise Exception(f"No repeat groups found in the specified SurveyCTO form.")

            return_dict = {}
            for repeat_group_name, repeat_group_url in repeat_groups_dict.items():
                data = (self._sesh.get(repeat_group_url)).text

                return_dict[repeat_group_name] = []

                csv_reader = csv.DictReader(io.StringIO(data))
                data_list = list(csv_reader)

                return_dict[repeat_group_name] = data_list

                yield return_dict  # json.dumps(return_dict, indent=2)

        except Exception as e:
            # Log the exception
            self.logger.exception(f"An error occurred: {str(e)}")
            # Raise the exception to stop the execution
            raise e
