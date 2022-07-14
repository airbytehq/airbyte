#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.states.state import State
from airbyte_cdk.sources.declarative.types import Config


def _get_max(*, name, val, other_state):
    other_val = other_state.get(name)
    if other_val:
        return max(val, other_val)
    else:
        return val


class StateType(Enum):
    STR = str
    INT = int


@dataclass
class DictState(State):
    stream_state_field = "stream_state"

    templates_to_evaluate: Mapping[str, str] = field(default_factory=dict)
    config: Config = field(default_factory=dict)

    def __post_init__(self):
        self._initial_mapping = self.templates_to_evaluate or dict()
        self.templates_to_evaluate = self._initial_mapping
        self._context = dict()
        self._interpolator = JinjaInterpolation()

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
