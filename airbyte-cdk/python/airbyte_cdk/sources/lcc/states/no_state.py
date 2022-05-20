#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.lcc.states.state import State


class NoState(State):
    def __init__(self, **kwargs):
        pass

    def update_state(self, **kwargs):
        pass

    def get_state(self):
        return {}
