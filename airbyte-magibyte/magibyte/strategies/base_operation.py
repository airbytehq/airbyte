from typing import Callable, Any


class BaseOperation(object):
    def __init__(self,
                 options: dict,
                 extrapolate: Callable[[str, dict], str],
                 strategy_builder: Callable[[str, dict, dict], Any]):
        self.options = options
        self.extrapolate = extrapolate
        self.strategy_builder = strategy_builder
