#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation
from airbyte_cdk.sources.cac.states.state import State


# FIXME: currently only support single values
class DictState(State):
    def __init__(self, name, value, state_type=str, vars=None, config=None):
        if vars is None:
            vars = dict()
        if config is None:
            config = dict()
        self._name = name
        self._value = value
        self._state_type = state_type
        self._interpolator = JinjaInterpolation()
        self._context = dict()
        self._vars = vars
        self._config = config

    def update_state(self, stream_slice, stream_state, last_response, last_record):
        prev_state = self.get_state()
        self._context.update(
            {"stream_slice": stream_slice, "stream_state": stream_state, "last_response": last_response, "last_record": last_record}
        )

        # self._state = self._compute_state(prev_state)
        self._context["stream_state"] = self._compute_state(prev_state)

    def get_state(self):
        return self._context.get("stream_state", {})

    def _compute_state(self, prev_state):
        # FIXME: date needs to be properly formatted!
        name = self._interpolator.eval(self._name, self._vars, self._config)
        val = self._interpolator.eval(self._value, self._vars, self._config, **self._context)
        if val:
            val = self._state_type(val)
        else:
            val = None

        if val is None:
            return prev_state

        if prev_state:
            val = self._get_max(val, name, prev_state)
        if self._context.get("stream_state"):
            val = self._get_max(val, name, self._context["stream_state"])

        updated_state = {name: val}
        self._context["stream_state"] = updated_state
        return {name: val}

    def _get_max(self, val, name, other_state):
        other_val = other_state.get(name)
        if other_val:
            return max(val, other_val)
        else:
            return val
