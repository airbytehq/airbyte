#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


def safe_max(arg1, arg2):
    if arg1 is None:
        return arg2
    if arg2 is None:
        return arg1
    return max(arg1, arg2)
