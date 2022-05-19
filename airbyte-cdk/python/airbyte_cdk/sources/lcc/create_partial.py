#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import inspect

from airbyte_cdk.sources.lcc.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.lcc.interpolation.jinja import JinjaInterpolation

"""
    Create a partial on steroids.
    Returns a partial object which when called will behave like func called with the arguments supplied.
    Parameters will be interpolated before the creation of the object
    The interpolation will take in kwargs, and config as parameters that can be accessed through interpolating.
    If any of the parameters are also create functions, they will also be created.
    kwargs are propagated to the recursive method calls
    :param func: Function
    :param args:
    :param keywords:
    :return: partially created object
    """


def create(func, /, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        interpolation = JinjaInterpolation()
        all_keywords = {**keywords}
        all_keywords.update(fkeywords)

        # config is a special keyword used for interpolation
        config = all_keywords.pop("config", None)

        # kwargs is a special keyword used for interpolation and propagation
        if "kwargs" in all_keywords:
            kwargs = all_keywords.pop("kwargs")
        else:
            kwargs = dict()

        # create object's partial parameters
        fully_created = _create_inner_objects(all_keywords, kwargs)

        # interpolate the parameters
        interpolated_keywords = InterpolatedMapping(fully_created, interpolation).eval(config, **{"kwargs": {**fully_created, **kwargs}})

        all_keywords.update(interpolated_keywords)

        # if config is not none, add it back to the keywords mapping
        if config is not None:
            all_keywords["config"] = config

        kwargs_to_pass_down = _get_kwargs_to_pass_to_func(func, kwargs)
        all_keywords_to_pass_down = _get_kwargs_to_pass_to_func(func, all_keywords)
        ret = func(*args, *fargs, **{**all_keywords_to_pass_down, **kwargs_to_pass_down})
        return ret

    newfunc.func = func
    newfunc.args = args
    newfunc.kwargs = keywords

    return newfunc


def _get_kwargs_to_pass_to_func(func, kwargs):
    kwargs_to_pass_down = set(inspect.getfullargspec(func).kwonlyargs)
    args_to_pass_down = set(inspect.getfullargspec(func).args)
    all_args = args_to_pass_down.union(kwargs_to_pass_down)
    kwargs_to_pass_down = {k: v for k, v in kwargs.items() if k in all_args}
    return kwargs_to_pass_down


def _create_inner_objects(keywords, kwargs):
    fully_created = dict()
    for k, v in keywords.items():
        if type(v) == type(create):
            fully_created[k] = v(kwargs=kwargs)
        else:
            fully_created[k] = v
    return fully_created
