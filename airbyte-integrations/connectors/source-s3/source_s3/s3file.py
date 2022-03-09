#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from contextlib import contextmanager
from typing import Any, BinaryIO, Iterator, TextIO, Union

import smart_open
from source_s3.s3_utils import make_s3_client

from .source_files_abstract.storagefile import StorageFile


class S3File(StorageFile):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @contextmanager
    def open(self, binary: bool) -> Iterator[Union[TextIO, BinaryIO]]:
        """
        Utilising smart_open to handle this (https://github.com/RaRe-Technologies/smart_open)

        :param binary: whether or not to open file as binary
        :return: file-like object
        """
        mode = "rb" if binary else "r"
        bucket = self._provider.get("bucket")
        params = {"client": make_s3_client(self._provider)}
        self.logger.debug(f"try to open {self.file_info}")
        result = smart_open.open(f"s3://{bucket}/{self.url}", transport_params=params, mode=mode)

        # see https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager for why we do this
        try:
            yield result
        finally:
            result.close()
