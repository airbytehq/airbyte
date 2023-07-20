#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from contextlib import contextmanager
from typing import Any, BinaryIO, Iterator, TextIO, Union

import smart_open
from source_s3.s3_utils import make_s3_client

from .source_files_abstract.storagefile import StorageFile


class S3File(StorageFile):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._client = make_s3_client(self._provider)

    @contextmanager
    def open(self, binary: bool) -> Iterator[Union[TextIO, BinaryIO]]:
        """
        Utilising smart_open to handle this (https://github.com/RaRe-Technologies/smart_open)

        :param binary: whether or not to open file as binary
        :return: file-like object
        """
        mode = "rb" if binary else "r"
        bucket = self._provider.get("bucket")
        params = {"client": self._client}
        self.logger.debug(f"try to open {self.file_info}")
        # There are rare cases when some keys become unreachable during sync
        # and we don't know about it, because catalog has been initially formed only once at the beginning
        # This is happen for example if a file was deleted/moved (or anything else) while we proceed with another file
        try:
            result = smart_open.open(f"s3://{bucket}/{self.url}", transport_params=params, mode=mode)
        except OSError as e:
            self.logger.warn(
                f"We don't have access to {self.url}. "
                f"Check whether key {self.url} exists in `{bucket}` bucket and/or has proper ACL permissions"
            )
            raise e
        # see https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager for why we do this
        try:
            yield result
        finally:
            result.close()
