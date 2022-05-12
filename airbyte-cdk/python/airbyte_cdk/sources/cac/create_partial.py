#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation
from airbyte_cdk.sources.cac.interpolation.interpolated_mapping import InterpolatedMapping


def create(func, /, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        interpolation = JinjaInterpolation()
        newkeywords = {**keywords}
        newkeywords.update(fkeywords)
        config = newkeywords.pop("config", None)
        if "kwargs" in newkeywords:
            kwargs = newkeywords.pop("kwargs")
        else:
            kwargs = dict()
        if "parent_kwargs" in newkeywords:
            parent_kwargs = newkeywords.pop("parent_kwargs")
        else:
            parent_kwargs = dict()

        fully_created = dict()
        for k, v in newkeywords.items():
            if type(v) == type(create):
                # keywords_without_k = {key: value for key, value in newkeywords.items() if key != k}
                fully_created[k] = v(parent_kwargs={**kwargs, **parent_kwargs})
            else:
                fully_created[k] = v

        interpolated_keywords = InterpolatedMapping(fully_created, interpolation).eval(
            config, **{"kwargs": {**fully_created, **parent_kwargs}}
        )
        newkeywords.update(interpolated_keywords)
        if config is not None:
            newkeywords["config"] = config
        print(f"ABOUT TO CREATE: {func}")
        ret = func(*args, *fargs, **{**newkeywords, **kwargs})
        return ret

    newfunc.func = func
    newfunc.args = args
    newfunc.kwargs = keywords

    return newfunc
