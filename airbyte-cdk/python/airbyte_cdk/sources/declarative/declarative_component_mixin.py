#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import Union


class DeclarativeComponentMixin:
    @classmethod
    def full_type_definition(cls):
        subclasses = cls.__subclasses__()
        print(f"subclasses for {cls}: {subclasses}")
        if subclasses:
            return Union[tuple(subclasses)]
        else:
            return cls
