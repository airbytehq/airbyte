#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.cac.states.no_state import NoState


def test():
    state = NoState()
    assert state.get_state() == {}
    state.update_state(None, {"date": "2021-01-01"}, None, None)
    assert state.get_state() == {}
