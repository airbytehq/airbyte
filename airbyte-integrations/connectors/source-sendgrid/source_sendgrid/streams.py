#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import math
import os
import time
import zlib
from abc import ABC
from contextlib import closing
from typing import Any, Iterable, List, Mapping, Optional, Tuple
from urllib.parse import urlparse

import pandas as pd
import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.rate_limiting import default_backoff_handler
from numpy import nan
from pendulum import DateTime
from requests import codes, exceptions


class SendgridStream(HttpStream, ABC):
    url_base = "https://api.sendgrid.com/"
    primary_key = "id"
    limit = 50
    data_field = None
    raise_on_http_errors = True
    permission_error_codes = {
        400: "authorization required",
        401: "authorization required",
    }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        pass  # not actually used because Contacts does read_records


class Contacts(SendgridStream):
    primary_key = "contact_id"
    MAX_RETRY_NUMBER = 3
    DEFAULT_WAIT_TIMEOUT_SECONDS = 60
    MAX_CHECK_INTERVAL_SECONDS = 2.0
    encoding = "utf-8"

    def path(self, **kwargs) -> str:
        return "v3/marketing/contacts/exports"

    @default_backoff_handler(max_tries=5, factor=15)
    def _send_http_request(self, method: str, url: str, stream: bool = False, enable_auth: bool = True):
        headers = self._session.auth.get_auth_header() if enable_auth else None
        response = self._session.request(method, url=url, headers=headers, stream=stream)
        if response.status_code not in [200, 202]:
            self.logger.error(f"error body: {response.text}")
        response.raise_for_status()
        return response

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        csv_urls, job_status = self.execute_export_job(url=f"{self.url_base}{self.path()}")
        if job_status == "failed":
            raise Exception(f"Export Job failed for more than 3 times, skipping reading stream {self.name}")
        for url in csv_urls:
            for record in self.read_with_chunks(*self.download_data(url=url)):
                yield record

    def execute_export_job(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        job_status = "failed"
        for i in range(0, self.MAX_RETRY_NUMBER):
            job_id = self.create_export_job(url=url)
            if not job_id:
                return None, job_status
            job_full_url = f"{url}/{job_id}"
            urls, job_status = self.wait_for_job(url=job_full_url)
            if urls:
                break
            self.logger.error(f"Waiting error. Try to run this job again {i + 1}/{self.MAX_RETRY_NUMBER}...")

        return urls, job_status

    def create_export_job(self, url: str) -> Optional[str]:
        """
        docs: https://docs.sendgrid.com/api-reference/contacts/export-contacts
        """
        try:
            response = self._send_http_request("POST", url)
            job_id: str = response.json().get("id")
            return job_id
        except exceptions.HTTPError as error:
            if error.response.status_code in [codes.BAD_REQUEST, codes.UNAUTHORIZED, codes.FORBIDDEN, codes.NOT_FOUND, codes.SERVER_ERROR]:
                error_data = error.response.json().get("errors")[0]
                error_id = error_data.get("error_id")
                error_message = error_data.get("message")
                error_parameter = error_data.get("parameter")
                self.logger.error(f"Cannot receive data for stream '{self.name}' ," f"{error_message=}, {error_id=}, {error_parameter=}")
            else:
                raise error
        return None

    def wait_for_job(self, url: str) -> Tuple[List[str], str]:
        """
        docs: https://docs.sendgrid.com/api-reference/contacts/export-contacts-status
        """
        expiration_time: DateTime = pendulum.now().add(seconds=self.DEFAULT_WAIT_TIMEOUT_SECONDS)
        job_status = "pending"
        urls: List[str] = []
        delay_timeout = 0.0
        delay_cnt = 0
        job_info = None
        time.sleep(0.5)
        while pendulum.now() < expiration_time:
            job_info = self._send_http_request("GET", url=url).json()
            job_status = job_info.get("status")
            urls = job_info.get("urls", [])
            if job_status in ("ready", "failure"):
                if job_status != "ready":
                    self.logger.error(f"JobStatus: {job_status}, error message: '{job_info}'")

                return urls, job_status

            if delay_timeout < self.MAX_CHECK_INTERVAL_SECONDS:
                delay_timeout = 0.5 + math.exp(delay_cnt) / 1000.0
                delay_cnt += 1

            time.sleep(delay_timeout)
            job_id = job_info["id"]
            self.logger.info(
                f"Sleeping {delay_timeout} seconds while waiting for Job: {self.name}/{job_id} to complete. Current state: {job_status}"
            )

        self.logger.warning(f"Not wait the {self.name} data for {self.DEFAULT_WAIT_TIMEOUT_SECONDS} seconds, data: {job_info}!!")
        return urls, job_status

    def download_data(self, url: str, chunk_size: int = 1024) -> tuple[str, str]:
        """
        Retrieves binary data result from successfully `executed_job`, using chunks, to avoid local memory limitations.
        Response received in .gzip binary format.
        @ url: string - the url of the `executed_job`
        @ chunk_size: int - the buffer size for each chunk to fetch from stream, in bytes, default: 1024 bytes
        Return the tuple containing string with file path of downloaded binary data (Saved temporarily) and file encoding.
        """
        # set filepath for binary data from response
        decompressor = zlib.decompressobj(zlib.MAX_WBITS | 32)

        url_parsed = urlparse(url)
        tmp_file = os.path.realpath(os.path.basename(url_parsed.path[1:-5]))
        download_session = requests.get(f"{url}", stream=True)
        with closing(download_session) as response, open(tmp_file, "wb") as data_file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                try:
                    # see if it's compressed. we are seeing some that are not all of a sudden.
                    # but let's also guard against the case where sendgrid changes it back.
                    data_file.write(decompressor.decompress(chunk))
                except zlib.error as e:
                    # it's not actually compressed!
                    data_file.write(chunk)
        # check the file exists
        if os.path.isfile(tmp_file):
            return tmp_file, self.encoding
        else:
            raise Exception(f"The IO/Error occured while verifying binary data. Stream: {self.name}, file {tmp_file} doesn't exist.")

    def read_with_chunks(self, path: str, file_encoding: str, chunk_size: int = 100) -> Iterable[Tuple[int, Mapping[str, Any]]]:
        """
        Reads the downloaded binary data, using lines chunks, set by `chunk_size`.
        @ path: string - the path to the downloaded temporarily binary data.
        @ file_encoding: string - encoding for binary data file according to Standard Encodings from codecs module
        @ chunk_size: int - the number of lines to read at a time, default: 100 lines / time.
        """
        try:
            with open(path, "r", encoding=file_encoding) as data:
                chunks = pd.read_csv(data, chunksize=chunk_size, iterator=True, dialect="unix", dtype=str)
                for chunk in chunks:
                    chunk = ({k.lower(): v for k, v in x.items()} for x in chunk.replace({nan: None}).to_dict(orient="records"))
                    for row in chunk:
                        yield row
        except pd.errors.EmptyDataError as e:
            self.logger.info(f"Empty data received. {e}")
            yield from []
        except IOError as ioe:
            raise Exception(f"The IO/Error occured while reading tmp data. Called: {path}. Stream: {self.name}", ioe)
        finally:
            # remove binary tmp file, after data is read
            os.remove(path)
