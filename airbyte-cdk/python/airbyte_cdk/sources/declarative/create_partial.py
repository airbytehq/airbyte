#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import inspect
from typing import Any, Mapping

PARAMETERS_STR = "$parameters"


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

        # $parameters is a special keyword used for interpolation and propagation
        if PARAMETERS_STR in all_keywords:
            parameters = all_keywords.get(PARAMETERS_STR)
        else:
            parameters = dict()

        # if config is not none, add it back to the keywords mapping
        if config is not None:
            all_keywords["config"] = config

        kwargs_to_pass_down = _get_kwargs_to_pass_to_func(func, parameters, all_keywords)
        all_keywords_to_pass_down = _get_kwargs_to_pass_to_func(func, all_keywords, all_keywords)

        # parameters is required as part of creation of all declarative components
        dynamic_args = {**all_keywords_to_pass_down, **kwargs_to_pass_down}
        if "parameters" not in dynamic_args:
            dynamic_args["parameters"] = {}
        else:
            # Handles the case where kwarg parameters and keyword $parameters both exist. We should merge both sets of parameters
            # before creating the component
            dynamic_args["parameters"] = {**all_keywords_to_pass_down["parameters"], **kwargs_to_pass_down["parameters"]}
        try:
            ret = func(*args, *fargs, **dynamic_args)
        except TypeError as e:
            raise Exception(f"failed to create object of type {func} because {e}")
        return ret

    newfunc.func = func
    newfunc.args = args
    newfunc.kwargs = keywords

    return newfunc


def _get_kwargs_to_pass_to_func(func, parameters, existing_keyword_parameters):
    argspec = inspect.getfullargspec(func)
    kwargs_to_pass_down = set(argspec.kwonlyargs)
    args_to_pass_down = set(argspec.args)
    all_args = args_to_pass_down.union(kwargs_to_pass_down)
    kwargs_to_pass_down = {
        k: v for k, v in parameters.items() if k in all_args and _key_is_unset_or_identical(k, v, existing_keyword_parameters)
    }
    if "parameters" in all_args:
        kwargs_to_pass_down["parameters"] = parameters
    return kwargs_to_pass_down


def _key_is_unset_or_identical(key: str, value: Any, mapping: Mapping[str, Any]):
    return key not in mapping or mapping[key] == value


def _create_inner_objects(keywords, kwargs):
    fully_created = dict()
    for k, v in keywords.items():
        if type(v) == type(create):
            fully_created[k] = v(kwargs=kwargs)
        else:
            fully_created[k] = v
    return fully_created
