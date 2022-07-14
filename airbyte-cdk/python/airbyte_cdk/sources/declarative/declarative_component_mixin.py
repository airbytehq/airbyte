#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import Union


class DeclarativeComponentMixin:
    @classmethod
    def full_type_definition(cls):
        subclasses = all_subclasses(cls)
        print(f"subclasses for {cls}: {subclasses}")
        if subclasses:
            return Union[tuple(subclasses)]
        else:
            return cls


def all_subclasses(cls):
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])
