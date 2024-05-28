#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
import io
from typing import Any, Mapping, Optional
import requests
import time
import logging
import json

from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState


@dataclass
class CustomRequester(HttpRequester):
    logger = logging.getLogger("airbyte")

    def __post_init__(self, parameters: Mapping[str, Any]):
        super(CustomRequester, self).__post_init__(parameters)
        self.fileId: str
        self.headers = {"X-API-Token": self.config["api_key"], "Content-Type": "application/json"}
        self.url = "https://fra1.qualtrics.com/API/v3"
        self.start_date: str

    def get_path(
        self,
        *,
        stream_state: Optional[StreamState],
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
    ) -> str:
        
        self.start_date = stream_slice["start_time"]
        stream_slice = stream_slice["id"]
        self.logger.info(f"Lets get responses for the survey: {stream_slice}")
        export_id = self._export_response(stream_slice)
        self.logger.info(f"Export id: {export_id}")
        self._check_progress(stream_slice, export_id)
        self.logger.info(f"File id: {self.fileId}")
        return f"surveys/{stream_slice}/export-responses/{self.fileId}/file"

    def _export_response(self, survey_id: str):
        url = f"{self.url}/surveys/{survey_id}/export-responses"
        try:
            response = requests.post(url, headers=self.headers, json={"format": "json", "compress":"false", "startDate": self.start_date, "sortByLastModifiedDate":"true"})
            response.raise_for_status()
            if response.status_code == 200:
                self.logger.info("Export and process_id retrieval succeeded")
                return response.json()["result"]["progressId"]
        except requests.exceptions.RequestException as e:
            raise self.logger.error(f"Error export : {e}")

    def _check_progress(self, survey_id: str, export_id: str, attempt=1):
        url = f"{self.url}/surveys/{survey_id}/export-responses/{export_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            if response.status_code == 200 and response.json()["result"]["status"] == "complete":
                self.logger.info("fileId retrieval succeeded")
                self.fileId = response.json()["result"]["fileId"]
            elif attempt < 100:
                self.logger.info(f"Attempt {attempt}: In Progress")
                attempt = attempt + 1
                time.sleep(10)
                self._check_progress(survey_id, export_id, attempt)
            else:
                raise self.logger.error(f"Reach maximum retry limit")
        except requests.exceptions.RequestException as e:
            raise self.logger.error(f"Error export : {e}")
        
    def _validate_response(
        self,
        response: requests.Response,
    ):
        response_dict = response.json()
        new_response_dict = dict()
        new_response_dict["responses"]=list()
        for e in response_dict["responses"]:
            e["_lastModifiedDate"]= e["values"]["_lastModifiedDate"]
            new_response_dict["responses"].append(e) 
        response._content = json.dumps(new_response_dict).encode('utf-8')
        return response
    