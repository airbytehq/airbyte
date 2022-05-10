#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation
from airbyte_cdk.sources.cac.states.state import State


# FIXME: currently only support single values
class DictState(State):
    def __init__(self, name, value, vars, config):
        self._name = name
        self._value = value
        self._interpolator = JinjaInterpolation()
        self._context = dict()
        self._vars = vars
        self._config = config

    def update_state(self, stream_slice, stream_state, last_response, last_record):
        self._context.update(
            {"stream_slice": stream_slice, "stream_state": stream_state, "last_response": last_response, "last_record": last_record}
        )

    def get_state(self):
        name = self._interpolator.eval(self._name, self._vars, self._config)
        val = self._interpolator.eval(self._value, self._vars, self._config, **self._context)
        prev_state = self._context.get("stream_state", {})
        if prev_state:
            prev_val = prev_state.get(name)
            if prev_val:
                val = max(val, prev_val)
        return {name: val}
