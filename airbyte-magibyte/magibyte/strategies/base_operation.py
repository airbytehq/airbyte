from typing import Callable, Any


class BaseOperation(object):
    def __init__(self,
                 options: dict,
                 extrapolate: Callable[[str, dict], str],
                 strategy_builder: Callable[[str, dict, dict], Any]):
        self.options = options
        self.extrapolate = extrapolate
        self.strategy_builder = strategy_builder

    def _build_step(self, name, **kwargs):
        config = self.options[name]
        return self.strategy_builder(config['strategy'], config.get('options', {}), **kwargs)
