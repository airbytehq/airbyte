# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import os
import uuid
from contextlib import closing
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import pandas as pd
import requests
from airbyte_cdk.sources.declarative.async_job.job import AsyncJob, AsyncJobStatus
from airbyte_cdk.sources.declarative.async_job.repository import AsyncJobRepository
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType
from numpy import nan
from requests import Response


@dataclass
class AsyncHttpJobRepository(AsyncJobRepository):
    create_job_requester: Requester
    polling_job_requester: Requester
    download_job_requester: Requester
    status_extractor: DpathExtractor
    status_mapping: Mapping[str, AsyncJobStatus]
    urls_extractor: DpathExtractor

    def __post_init__(self) -> None:
        self._create_job_response_by_id: Dict[str, Response] = {}
        self._polling_job_response_by_id: Dict[str, Response] = {}

        self._DEFAULT_ENCODING = "utf-8"
        self._DOWNLOAD_CHUNK_SIZE = 1024 * 1024 * 10

    def start(self, stream_slice: StreamSlice) -> AsyncJob:
        response: Optional[requests.Response] = self.create_job_requester.send_request(stream_slice=stream_slice)
        if not response:
            raise AirbyteTracedException(
                internal_message="Always expect a response or an exception from create_job_requester",
                failure_type=FailureType.system_error,
            )

        job_id: str = str(uuid.uuid4())  # FIXME is there value to extract the id from the response?
        self._create_job_response_by_id[job_id] = response

        return AsyncJob(api_job_id=job_id, job_parameters=stream_slice)

    def update_jobs_status(self, jobs: Iterable[AsyncJob]) -> None:
        for job in jobs:
            polling_response: requests.Response = self.polling_job_requester.send_request(
                stream_slice=StreamSlice(
                    partition={"create_job_response": self._create_job_response_by_id[job.api_job_id()]}, cursor_slice={}
                )
            )
            api_status = next(  # type: ignore  # the typing is really weird here but it does not extract records but any and we assume the connector developer has configured this properly
                self.status_extractor.extract_records(polling_response), None
            )
            job_status = self.status_mapping.get(api_status, None)
            if job_status is None:
                raise ValueError(
                    f"API status `{api_status}` is unknown. Contact the connector developer to make sure this status is supported."
                )
            job.update_status(job_status)

            if job_status == AsyncJobStatus.COMPLETED:
                self._polling_job_response_by_id[job.api_job_id()] = polling_response

    def fetch_records(self, job: AsyncJob) -> Iterable[Mapping[str, Any]]:
        url: str
        for url in self.urls_extractor.extract_records(self._polling_job_response_by_id[job.api_job_id()]):  # type: ignore  # the typing is really weird here but it does not extract records but any and we assume the connector developer has configured this properly
            # FIXME salesforce will require pagination here
            file_path, encoding = self._download_to_file(url)
            print("downloaded")
            yield from self._read_with_chunks(file_path, encoding)

        yield from []

        # clean self._create_job_response_by_id and self._polling_job_response_by_id

    def _download_to_file(self, url: str) -> Tuple[str, str]:
        tmp_file = str(uuid.uuid4())
        streamed_response = self.download_job_requester.send_request(stream_slice=StreamSlice(partition={"url": url}, cursor_slice={}))
        with closing(streamed_response) as response, open(tmp_file, "wb") as data_file:
            response_encoding = self._get_response_encoding(response.headers or {})
            for chunk in response.iter_content(chunk_size=self._DOWNLOAD_CHUNK_SIZE):
                data_file.write(self._filter_null_bytes(chunk))
        # check the file exists
        if os.path.isfile(tmp_file):
            return tmp_file, response_encoding
        else:
            raise ValueError(f"The IO/Error occured while verifying binary data. Tmp file {tmp_file} doesn't exist.")

    def _get_response_encoding(self, headers: Dict[str, Any]) -> str:
        """Returns encodings from given HTTP Header Dict.

        :param headers: dictionary to extract encoding from.
        :rtype: str
        """

        content_type = headers.get("content-type")

        if not content_type:
            return self._DEFAULT_ENCODING

        content_type, params = requests.utils._parse_content_type_header(content_type)

        if "charset" in params:
            # FIXME this was part of salesforce code but it is unclear why it is needed (see https://airbytehq-team.slack.com/archives/C02U9R3AF37/p1724693926504639)
            return params["charset"].strip("'\"")

        return self._DEFAULT_ENCODING

    def _filter_null_bytes(self, b: bytes):
        """
        https://github.com/airbytehq/airbyte/issues/8300
        """
        res = b.replace(b"\x00", b"")
        if len(res) < len(b):
            pass
            # FIXME self.logger.warning("Filter 'null' bytes from string, size reduced %d -> %d chars", len(b), len(res))
        return res

    def _read_with_chunks(self, path: str, file_encoding: str, chunk_size: int = 100) -> Iterable[Mapping[str, Any]]:
        """
        Reads the downloaded binary data, using lines chunks, set by `chunk_size`.
        @ path: string - the path to the downloaded temporarily binary data.
        @ file_encoding: string - encoding for binary data file according to Standard Encodings from codecs module
        @ chunk_size: int - the number of lines to read at a time, default: 100 lines / time.
        """
        try:
            with open(path, "r", encoding=file_encoding) as data:
                chunks = pd.read_csv(data, chunksize=chunk_size, iterator=True, dialect="unix", dtype=object)
                for chunk in chunks:
                    chunk = chunk.replace({nan: None}).to_dict(orient="records")
                    for row in chunk:
                        yield row
        except pd.errors.EmptyDataError as e:
            # FIXME logger.info(f"Empty data received. {e}")
            yield from []
        except IOError as ioe:
            raise ValueError(f"The IO/Error occured while reading tmp data. Called: {path}", ioe)
        finally:
            # remove binary tmp file, after data is read
            os.remove(path)
