#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import abc
from typing import Any, Dict

from airbyte_cdk.test.mock_http import HttpResponse


class AbstractResponseBuilder(abc.ABC):
    @abc.abstractmethod
    def build(self) -> HttpResponse:
        pass
