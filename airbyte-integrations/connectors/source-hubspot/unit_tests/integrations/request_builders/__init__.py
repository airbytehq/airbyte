# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import abc


class AbstractRequestBuilder:
    @abc.abstractmethod
    def build(self):
        pass
