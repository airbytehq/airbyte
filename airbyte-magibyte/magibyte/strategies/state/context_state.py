from magibyte.strategies.state.base_state import BaseState


class ContextState(BaseState):
    def get(self, context):
        name = self.extrapolate(self.options['name'], context)
        value = self.extrapolate(self.options['value'], context)

        return {name: value}
