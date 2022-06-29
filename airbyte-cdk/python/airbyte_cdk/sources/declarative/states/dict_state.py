#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from enum import Enum
from typing import Mapping

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.states.state import State


def _get_max(*, name, val, other_state):
    other_val = other_state.get(name)
    if other_val:
        return max(val, other_val)
    else:
        return val


class StateType(Enum):
    STR = str
    INT = int


class DictState(State):
    stream_state_field = "stream_state"

    def __init__(self, initial_mapping: Mapping[str, str] = None, config=None):
        if initial_mapping is None:
            initial_mapping = dict()
        if config is None:
            config = dict()
        self._templates_to_evaluate = initial_mapping
        self._interpolator = JinjaInterpolation()
        self._context = dict()
        self._config = config

    def set_state(self, state):
        self._context[self.stream_state_field] = state

    def update_state(self, **kwargs):
        stream_state = kwargs.get(self.stream_state_field)
        prev_stream_state = self.get_stream_state() or stream_state
        self._context.update(**kwargs)

        self._context[self.stream_state_field] = self._compute_state(prev_stream_state)

    def get_state(self, state_field):
        return self._context.get(state_field, {})

    def get_stream_state(self):
        return self.get_state(self.stream_state_field)

    def _compute_state(self, prev_state):
        updated_state = {
            self._interpolator.eval(name, self._config): self._interpolator.eval(value, self._config, **self._context)
            for name, value in self._templates_to_evaluate.items()
        }
        updated_state = {name: value for name, value in updated_state.items() if value}

        if prev_state:
            next_state = {name: _get_max(name=name, val=value, other_state=prev_state) for name, value in updated_state.items()}
        else:
            next_state = updated_state

        self._context[self.stream_state_field] = next_state
        return next_state
