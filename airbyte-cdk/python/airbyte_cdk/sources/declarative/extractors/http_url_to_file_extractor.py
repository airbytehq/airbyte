#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import uuid
import zlib
from contextlib import closing
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import pandas as pd
import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from numpy import nan

EMPTY_STR: str = ""
DEFAULT_ENCODING: str = "utf-8"
DOWNLOAD_CHUNK_SIZE: int = 1024 * 1024 * 10


@dataclass
class HttpUrlToFileExtractor(RecordExtractor):
    def _get_response_encoding(self, headers: Dict[str, Any]) -> str:
        """
        Get the encoding of the response based on the provided headers.
        Args:
            headers (Dict[str, Any]): The headers of the response.
        Returns:
            str: The encoding of the response.
        """

        content_type = headers.get("content-type")

        if not content_type:
            return DEFAULT_ENCODING

        content_type, params = requests.utils.parse_header_links(content_type)

        if "charset" in params:
            # FIXME this was part of salesforce code but it is unclear why it is needed (see https://airbytehq-team.slack.com/archives/C02U9R3AF37/p1724693926504639)
            return params["charset"].strip("'\"")

        return DEFAULT_ENCODING

    def _filter_null_bytes(self, b: bytes) -> bytes:
        """
        Filter out null bytes from a bytes object.
        Args:
            b (bytes): The input bytes object.
        Returns:
            bytes: The filtered bytes object with null bytes removed.

        Referenced Issue:
            https://github.com/airbytehq/airbyte/issues/8300
        """

        res = b.replace(b"\x00", b"")
        if len(res) < len(b):
            pass
            # FIXME self.logger.warning("Filter 'null' bytes from string, size reduced %d -> %d chars", len(b), len(res))
        return res

    def _save_to_file(self, response: Optional[requests.Response] = None) -> Tuple[str, str]:
        """
        Saves the binary data from the given response to a temporary file and returns the filepath and response encoding.

        Args:
            response (Optional[requests.Response]): The response object containing the binary data. Defaults to None.

        Returns:
            Tuple[str, str]: A tuple containing the filepath of the temporary file and the response encoding.

        Raises:
            ValueError: If the temporary file does not exist after saving the binary data.
        """
        # set filepath for binary data from response
        decompressor = zlib.decompressobj(zlib.MAX_WBITS | 32)

        if response:
            tmp_file = str(uuid.uuid4())
            with closing(response) as response, open(tmp_file, "wb") as data_file:
                response_encoding = self._get_response_encoding(dict(response.headers or {}))
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    try:
                        data_file.write(decompressor.decompress(chunk))
                    except zlib.error:
                        # we bypass having the context of the error here,
                        # since it's just a flag-type exception to handle a different scenario.
                        data_file.write(self._filter_null_bytes(chunk))

            # check the file exists
            if os.path.isfile(tmp_file):
                return tmp_file, response_encoding
            else:
                raise ValueError(f"The IO/Error occured while verifying binary data. Tmp file {tmp_file} doesn't exist.")

        # return default values
        return EMPTY_STR, EMPTY_STR

    def _read_with_chunks(self, path: str, file_encoding: str, chunk_size: int = 100) -> Iterable[Mapping[str, Any]]:
        """
        Reads data from a file in chunks and yields each row as a dictionary.

        Args:
            path (str): The path to the file to be read.
            file_encoding (str): The encoding of the file.
            chunk_size (int, optional): The size of each chunk to be read. Defaults to 100.

        Yields:
            Mapping[str, Any]: A dictionary representing each row of data.

        Raises:
            ValueError: If an IO/Error occurs while reading the temporary data.
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

    def extract_records(self, response: Optional[requests.Response] = None) -> Iterable[Mapping[str, Any]]:
        """
        Extracts records from the given response by:
            1) Saving the result to a tmp file
            2) Reading from saved file by chunks to avoid OOM

        Args:
            response (Optional[requests.Response]): The response object containing the data. Defaults to None.

        Yields:
            Iterable[Mapping[str, Any]]: An iterable of mappings representing the extracted records.

        Returns:
            None
        """

        # FIXME salesforce will require pagination here

        if response:
            file_path, encoding = self._save_to_file(response)
            yield from self._read_with_chunks(file_path, encoding)
        else:
            yield from []
