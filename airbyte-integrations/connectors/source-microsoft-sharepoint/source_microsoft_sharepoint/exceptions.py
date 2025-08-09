# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from airbyte_cdk.sources.file_based.exceptions import BaseFileBasedSourceError


class ErrorFetchingMetadata(BaseFileBasedSourceError):
    pass


class ErrorDownloadingFile(BaseFileBasedSourceError):
    pass
