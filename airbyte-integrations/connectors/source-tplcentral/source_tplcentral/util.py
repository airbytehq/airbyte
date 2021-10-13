from collections import abc
from airbyte_cdk.sources.utils.casing import camel_to_snake

def deep_map(function, d):
    if isinstance(d, list):
        return list(map(lambda v: deep_map(function, v), d))

    d = function(d)
    for key, val in d.items():
        if isinstance(val, dict):
            d[key] = deep_map(function, val)
        else:
            d[key] = val
    return d

def normalize(d):
    return deep_map(_normalizer, d)

def _normalizer(d):
    out = {}
    for k, v in d.items():
        if not k == '_links':
            out[camel_to_snake(k)] = v
    return out
