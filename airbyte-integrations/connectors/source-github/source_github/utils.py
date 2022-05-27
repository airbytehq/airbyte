#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


def getter(D: dict, key_or_keys):
    if not isinstance(key_or_keys, list):
        key_or_keys = [key_or_keys]
    for k in key_or_keys:
        D = D[k]
    return D
