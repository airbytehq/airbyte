#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from io import IOBase
from io import StringIO
import json
import os
from typing import Iterable, List, Optional, Set


from airbyte_cdk.sources.file_based.file_based_stream_reader import FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile

from source_s3.v4.config import Config
from source_s3.v4.stream_reader import SourceS3StreamReader


class SourceS3BulkStreamReader(SourceS3StreamReader):
    def __init__(self):
        super().__init__()


    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        full_file_uri = f"s3://{self.config.bucket}/{file.uri}"
        record = {
            "file_uri": full_file_uri,
            "file_name": os.path.basename(full_file_uri),
        }

        json_string = json.dumps(record)
        string_io = StringIO(json_string)
        # Now, `string_io` is a file-like object containing the JSON data.
        # You can use it as you would with any file-like object.
        # The JSONL parser will read the data from it.
        return string_io

