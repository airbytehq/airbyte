#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import os
import shutil
import uuid
from typing import BinaryIO, Optional, TextIO, Union

import dagster._check as check
from dagster._core.storage.file_manager import LocalFileHandle, LocalFileManager, check_file_like_obj
from dagster._utils import mkdir_p
from typing_extensions import TypeAlias


IOStream: TypeAlias = Union[TextIO, BinaryIO]


class SimpleLocalFileManager(LocalFileManager):
    """
    HACK WARNING: This is a hack to get around the fact that the LocalFileManager in dagster does not
    expose the key parameter and does not handle nested directories.

    Much of this code is borrowed from the LocalFileManager in dagster and modified slightly.

    https://docs.dagster.io/_modules/dagster/_core/storage/file_manager#local_file_manager
    """

    def ensure_dir_exists_for_file(self, file_path: str):
        self.ensure_base_dir_exists()
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            mkdir_p(dir_path)

    def write_data(self, data: bytes, key: Optional[str] = None, ext: Optional[str] = None):
        check.inst_param(data, "data", bytes)
        return self.write(io.BytesIO(data), mode="wb", key=key, ext=ext)

    def write(self, file_obj: IOStream, mode: str = "wb", key: Optional[str] = None, ext: Optional[str] = None) -> LocalFileHandle:
        check_file_like_obj(file_obj)
        check.opt_str_param(key, "key")
        check.opt_str_param(ext, "ext")

        file_name = key if key is not None else str(uuid.uuid4())

        dest_file_path = os.path.join(self.base_dir, file_name + (("." + ext) if ext is not None else ""))

        self.ensure_dir_exists_for_file(dest_file_path)

        encoding = None if "b" in mode else "utf8"
        with open(dest_file_path, mode, encoding=encoding) as dest_file_obj:
            shutil.copyfileobj(file_obj, dest_file_obj)
            return LocalFileHandle(dest_file_path)
