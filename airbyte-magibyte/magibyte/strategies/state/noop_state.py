from magibyte.strategies.state.base_state import BaseState


class NoopState(BaseState):
    def get(self, context):
        return None
