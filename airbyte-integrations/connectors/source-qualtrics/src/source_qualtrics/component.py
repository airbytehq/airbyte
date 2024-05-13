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
        self.fileId: str
        self.headers = {"X-API-Token": self.config["api_key"], "Content-Type": "application/json"}
        self.url = "https://fra1.qualtrics.com/API/v3"

    def get_path(
        self,
        *,
        stream_state: Optional[StreamState],
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
    ) -> str:
        """
        Returns the URL path for the API endpoint e.g: if you wanted to hit https://myapi.com/v1/some_entity then this should return "some_entity"
        """
        stream_slice = stream_slice["id"]
        export_id = self._export_response(stream_slice)
        self._check_progress(stream_slice, export_id)
        return f"surveys/{stream_slice}/export-responses/{self.fileId}/file"

    def _export_response(self, survey_id: str):
        url = f"{self.url}//surveys/{survey_id}/export-responses"
        try:
            response = requests.post(url, headers=self.headers, json={"format": "json", "compress": "false"})
            response.raise_for_status()
            if response.status_code == 200:
                print("Export and process id_retrieval succeeded")
                return response.json()["result"]["progressId"]
        except requests.exceptions.RequestException as e:
            raise SystemExit(f"Error export : {e}")

    def _check_progress(self, survey_id: str, export_id: str, attempt=1):
        url = f"{self.url}/surveys/{survey_id}/export-responses/{export_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            if response.status_code == 200 and response.json()["result"]["status"] == "complete":
                print("fileId retrieval succeeded")
                self.fileId = response.json()["result"]["fileId"]
            elif attempt < 20:
                print(f"Attempt {attempt}: In Progress")
                attempt = attempt + 1
                time.sleep(30)
                self._check_progress(survey_id, export_id, attempt)
            else:
                raise SystemExit(f"Reach maximum retry limit")
        except requests.exceptions.RequestException as e:
            raise SystemExit(f"Error export : {e}")
