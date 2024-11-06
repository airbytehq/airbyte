# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any

from airbyte_cdk.sources.file_based.stream import DefaultFileBasedStream
from source_gcs.helpers import GCSRemoteFile


class GCSStream(DefaultFileBasedStream):
    def transform_record(self, record: dict[str, Any], file: GCSRemoteFile, last_updated: str) -> dict[str, Any]:
        record[self.ab_last_mod_col] = last_updated
        record[self.ab_file_name_col] = file.displayed_uri if file.displayed_uri else file.uri
        return record
