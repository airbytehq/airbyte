import importlib

from magibyte.core.extrapolation import extrapolate


class BaseOperation(object):
    def __init__(self, options, **kwargs):
        self.options = options
        self.extrapolate = kwargs.get('extrapolator', extrapolate)

    @classmethod
    def build_strategy(cls, strategy_type, config, **kwargs):
        strategy_name = config['strategy']
        strategy_options = config.get('options', {})

        klass = BaseOperation._get_strategy_class(strategy_type, strategy_name)

        return klass(strategy_options, **kwargs)

    @classmethod
    def _get_strategy_class(cls, strategy_type: str, strategy_name: str):
        if '.' not in strategy_name:
            strategy_name = f"magybite.strategies.{strategy_type}.{strategy_name}"

        split = strategy_name.split('.')
        return getattr(importlib.import_module('.'.join(split[:-1])), split[-1])
