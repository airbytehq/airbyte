#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import inspect
from typing import Any, Mapping

OPTIONS_STR = "$options"


def create(func, /, *args, **keywords):
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

    def newfunc(*fargs, **fkeywords):
        all_keywords = {**keywords}
        all_keywords.update(fkeywords)

        # config is a special keyword used for interpolation
        config = all_keywords.pop("config", None)

        # $options is a special keyword used for interpolation and propagation
        if OPTIONS_STR in all_keywords:
            options = all_keywords.get(OPTIONS_STR)
        else:
            options = dict()

        # if config is not none, add it back to the keywords mapping
        if config is not None:
            all_keywords["config"] = config

        kwargs_to_pass_down = _get_kwargs_to_pass_to_func(func, options)
        all_keywords_to_pass_down = _get_kwargs_to_pass_to_func(func, all_keywords)

        # options is a required input for all declarative components
        dynamic_args = {**all_keywords_to_pass_down, **kwargs_to_pass_down}
        if "options" not in dynamic_args:
            dynamic_args["options"] = {}
        else:
            dynamic_args["options"] = _merge_options(all_keywords_to_pass_down["options"], kwargs_to_pass_down["options"])
        try:
            ret = func(*args, *fargs, **dynamic_args)
        except TypeError as e:
            raise Exception(f"failed to create object of type {func} because {e}")
        return ret

    newfunc.func = func
    newfunc.args = args
    newfunc.kwargs = keywords

    return newfunc


def _get_kwargs_to_pass_to_func(func, options):
    argspec = inspect.getfullargspec(func)
    kwargs_to_pass_down = set(argspec.kwonlyargs)
    args_to_pass_down = set(argspec.args)
    all_args = args_to_pass_down.union(kwargs_to_pass_down)
    kwargs_to_pass_down = {k: v for k, v in options.items() if k in all_args}
    if "options" in all_args:
        kwargs_to_pass_down["options"] = options
    return kwargs_to_pass_down


def _create_inner_objects(keywords, kwargs):
    fully_created = dict()
    for k, v in keywords.items():
        if type(v) == type(create):
            fully_created[k] = v(kwargs=kwargs)
        else:
            fully_created[k] = v
    return fully_created


# To handle the case where kwarg options and keyword $options both exist, we should merge both sets of options before creating a component
def _merge_options(m1: Mapping[str, Any], m2: Mapping[str, Any]) -> Mapping[str, Any]:
    return {**m1, **m2}
