#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional, Union

from airbyte_cdk import AirbyteTracedException, FailureType

from .source_files_abstract.file_info import FileInfo


class S3Exception(AirbyteTracedException):
    def __init__(
        self,
        file_info: Union[List[FileInfo], FileInfo],
        internal_message: Optional[str] = None,
        message: Optional[str] = None,
        failure_type: FailureType = FailureType.system_error,
        exception: BaseException = None,
    ):
        file_info = (
            file_info
            if isinstance(file_info, (list, tuple))
            else [
                file_info,
            ]
        )
        file_names = ", ".join([file.key for file in file_info])
        user_friendly_message = f"""
        The connector encountered an error while processing the file(s): {file_names}.
        {message}
        This can be an input configuration error as well, please double check your connection settings.
        """
        super().__init__(internal_message=internal_message, message=user_friendly_message, failure_type=failure_type, exception=exception)
