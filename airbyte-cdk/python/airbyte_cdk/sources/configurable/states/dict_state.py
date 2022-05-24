#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from enum import Enum
from typing import Mapping

from airbyte_cdk.sources.configurable.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.configurable.states.state import State


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
    def __init__(self, d: Mapping[str, str] = None, state_type="STR", config=None):
        if d is None:
            d = dict()
        if config is None:
            config = dict()
        self._d = d
        if type(state_type) == str:
            self._state_type = StateType[state_type].value
        elif type(state_type) == type:
            self._state_type = state_type
        elif type(state_type) == type:
            self._state_type = state_type
        else:
            raise Exception(f"Unexpected type for state_type. Got {state_type}")
        self._interpolator = JinjaInterpolation()
        self._context = dict()
        self._config = config

    def update_state(self, **kwargs):
        stream_state = kwargs.get("stream_state")
        prev_state = self.get_state() or stream_state
        self._context.update(**kwargs)

        self._context["stream_state"] = self._compute_state(prev_state)

    def get_context(self):
        return self._context

    def get_state(self):
        return self._context.get("stream_state", {})

    def _compute_state(self, prev_state):
        updated_state = {
            self._interpolator.eval(name, self._config): self._interpolator.eval(value, self._config, **self._context)
            for name, value in self._d.items()
        }
        updated_state = {name: self._state_type(value) for name, value in updated_state.items() if value}

        if prev_state:
            next_state = {name: _get_max(name=name, val=value, other_state=prev_state) for name, value in updated_state.items()}
        else:
            next_state = updated_state

        self._context["stream_state"] = next_state
        return next_state
