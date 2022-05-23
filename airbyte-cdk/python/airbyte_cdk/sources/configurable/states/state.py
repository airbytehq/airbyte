#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import copy
from abc import ABC, abstractmethod
from typing import Any, Mapping

import requests
from airbyte_cdk.sources.configurable.types import Record


class State(ABC):
    @abstractmethod
    def update_state(
        self, *stream_slice: Mapping[str, Any], stream_state: Mapping[str, Any], last_response: requests.Response, last_record: Record
    ):
        pass

    @abstractmethod
    def get_state(self):
        pass

    def deep_copy(self):
        return copy.deepcopy(self)
