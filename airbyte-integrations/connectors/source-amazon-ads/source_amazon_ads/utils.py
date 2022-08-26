#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


def iterate_one_by_one(*iterables):
    iterables = list(iterables)
    while iterables:
        iterable = iterables.pop(0)
        try:
            yield next(iterable)
        except StopIteration:
            pass
        else:
            iterables.append(iterable)
