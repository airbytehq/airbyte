#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
from abc import ABC, abstractmethod

from airbyte_cdk.sources.declarative.declarative_component_mixin import DeclarativeComponentMixin


class State(ABC, DeclarativeComponentMixin):
    @abstractmethod
    def update_state(self, **kwargs):
        pass

    @abstractmethod
    def get_stream_state(self):
        pass

    def deep_copy(self):
        return copy.deepcopy(self)
