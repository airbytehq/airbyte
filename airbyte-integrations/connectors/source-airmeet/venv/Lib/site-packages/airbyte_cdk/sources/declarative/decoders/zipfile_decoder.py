#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
import zipfile
from dataclasses import dataclass
from io import BytesIO

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.decoders import Decoder
from airbyte_cdk.sources.declarative.decoders.composite_raw_decoder import Parser
from airbyte_cdk.sources.declarative.decoders.decoder import DECODER_OUTPUT_TYPE
from airbyte_cdk.utils import AirbyteTracedException

logger = logging.getLogger("airbyte")


@dataclass
class ZipfileDecoder(Decoder):
    parser: Parser

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> DECODER_OUTPUT_TYPE:
        try:
            with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
                for file_name in zip_file.namelist():
                    unzipped_content = zip_file.read(file_name)
                    buffered_content = BytesIO(unzipped_content)
                    try:
                        yield from self.parser.parse(
                            buffered_content,
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to parse file: {file_name} from zip file: {response.request.url} with exception {e}."
                        )
                        raise AirbyteTracedException(
                            message=f"Failed to parse file: {file_name} from zip file.",
                            internal_message=f"Failed to parse file: {file_name} from zip file: {response.request.url}.",
                            failure_type=FailureType.system_error,
                        ) from e
        except zipfile.BadZipFile as e:
            logger.error(
                f"Received an invalid zip file in response to URL: {response.request.url}. "
                f"The size of the response body is: {len(response.content)}"
            )
            raise AirbyteTracedException(
                message="Received an invalid zip file in response.",
                internal_message=f"Received an invalid zip file in response to URL: {response.request.url}.",
                failure_type=FailureType.system_error,
            ) from e
