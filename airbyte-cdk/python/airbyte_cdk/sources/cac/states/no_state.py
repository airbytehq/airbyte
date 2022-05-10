#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.cac.states.state import State


class NoState(State):
    def __init__(self, **kwargs):
        pass

    def update_state(self, stream_slice, stream_state, last_response, last_record):
        pass

    def get_state(self):
        return {}
