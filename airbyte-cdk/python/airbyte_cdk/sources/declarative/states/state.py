#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def update_state(self, **kwargs):
        pass

    @abstractmethod
    def get_stream_state(self):
        pass

    def deep_copy(self):
        return copy.deepcopy(self)
