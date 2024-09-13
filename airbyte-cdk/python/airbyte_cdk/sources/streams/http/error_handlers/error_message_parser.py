#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Optional

import requests


class ErrorMessageParser(ABC):
    @abstractmethod
    def parse_response_error_message(self, response: requests.Response) -> Optional[str]:
        """
        Parse error message from response.
        :param response: response received for the request
        :return: error message
        """
        pass
