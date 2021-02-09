import importlib


def build(strategy_name, strategy_options, **kwargs):
    new_kwargs = kwargs.copy()
    new_kwargs['options'] = strategy_options

    split = strategy_name.split('.')
    klass = getattr(importlib.import_module('.'.join(split[:-1])), split[-1])

    return klass(**new_kwargs)
