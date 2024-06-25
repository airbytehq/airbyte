# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import abc

from airbyte_cdk.test.mock_http import HttpResponse


class AbstractResponseBuilder:
    @abc.abstractmethod
    def build(self) -> HttpResponse:
        pass
