#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import copy
from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def update_state(self, stream_slice, stream_state, last_response, last_record):
        # FIXME: Add types
        pass

    @abstractmethod
    def get_state(self):
        pass

    def copy(self):
        return copy.deepcopy(self)
