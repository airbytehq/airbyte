#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Optional

from airbyte_cdk.sources.streams import Stream


class ErrorMessageParser(ABC):
    @abstractmethod
    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """

        :param exception:
        :return:
        """


class LegacyErrorMessageParser(ErrorMessageParser):
    def __init__(self, stream: Stream):
        self._stream = stream

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        return self._stream.get_error_display_message(exception)
