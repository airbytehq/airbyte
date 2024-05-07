#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from datetime import datetime
from functools import partial
import os
from typing import Any, Mapping, MutableMapping, Optional, Type, Union
import requests
import time

from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class CustomRequester(HttpRequester):



    def __post_init__(self, parameters: Mapping[str, Any]):
        super(CustomRequester, self).__post_init__(parameters)
        self.headers = {
            "X-API-Token": self.config['api_key'],
            "Content-Type": "application/json"
        }
 

    def get_url_base(self) -> str:
        return os.path.join(self._url_base.eval(self.config), "")
    
    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        headers = super().get_request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return headers
    

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        """
        Combines queries to a single GraphQL query.
        """
        export_id = self._export_response(stream_slice['id'])
        export_id = "ES_5mR6q6us6Lsuyqy"
        fileId = self._check_progress(stream_slice['id'], export_id)
        print(fileId)


    def _export_response(self, survey_id:str):
        url = f"https://fra1.qualtrics.com/API/v3/surveys/{survey_id}/export-responses"
        try:
            response = requests.post(url, headers=self.headers, json={"format": "csv"})
            response.raise_for_status()
            if response.status_code == 200:
                print("Export and process id_retrieval succeeded")
                return response.json()['result']["progressId"]
        except requests.exceptions.RequestException as e:
            raise SystemExit(f"Error export : {e}")


    def _check_progress(self, survey_id:str, export_id:str):
        url = f"https://fra1.qualtrics.com/API/v3/surveys/{survey_id}/export-responses/{export_id}"
        try:
            response = requests.get(url, headers=self.headers, json={"format": "csv"})
            response.raise_for_status()
            if response.status_code == 200 and response.json()['result']["status"]=="complete":
                print("fileId retrieval succeeded")
                return response.json()['result']["fileId"]
            else:
                print("in Progress")
                time.sleep(30)
                self._check_progress(survey_id, export_id)
        except requests.exceptions.RequestException as e:
            raise SystemExit(f"Error export : {e}")
        response = requests.get(url, headers=self.headers, json={})

    def _get_response(self, survey_id:str, file_id:str):
        url = f"https://fra1.qualtrics.com/API/v3/surveys/{survey_id}/export-responses/{file_id}/file"
        try:
            response = requests.get(url, headers=self.headers, json={"format": "csv"})
            response.raise_for_status()
            if response.status_code == 200 :
                print("fileId retrieval succeeded")
                return response.json()['result']["fileId"]
        except requests.exceptions.RequestException as e:
            raise SystemExit(f"Error export : {e}")
        response = requests.get(url, headers=self.headers, json={})