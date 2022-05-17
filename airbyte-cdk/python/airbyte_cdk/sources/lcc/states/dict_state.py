#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Mapping

from airbyte_cdk.sources.lcc.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.lcc.states.state import State


def _get_max(*, name, val, other_state):
    other_val = other_state.get(name)
    if other_val:
        return max(val, other_val)
    else:
        return val


class DictState(State):
    def __init__(self, d: Mapping[str, str] = None, state_type=str, config=None):
        if d is None:
            d = dict()
        if config is None:
            config = dict()
        self._d = d
        self._state_type = state_type
        self._interpolator = JinjaInterpolation()
        self._context = dict()
        self._config = config

    def update_state(self, stream_slice, stream_state, last_response, last_record):
        prev_state = self.get_state() or stream_state
        self._context.update(
            {"stream_slice": stream_slice, "stream_state": stream_state, "last_response": last_response, "last_record": last_record}
        )

        self._context["stream_state"] = self._compute_state(prev_state)

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
