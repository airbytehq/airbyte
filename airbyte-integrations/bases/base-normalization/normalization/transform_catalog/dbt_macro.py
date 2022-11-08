#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod


class Macro(ABC):
    "https://docs.getdbt.com/docs/building-a-dbt-project/jinja-macros"

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        return str(self) + str(other)

    def __radd__(self, other):
        return str(other) + str(self)


class Source(Macro):
    "https://docs.getdbt.com/reference/dbt-jinja-functions/source"

    def __init__(self, source_name: str, table_name: str):
        self.source_name = source_name
        self.table_name = table_name

    def __str__(self):
        return "source('{}', '{}')".format(self.source_name, self.table_name)


class Ref(Macro):
    "https://docs.getdbt.com/reference/dbt-jinja-functions/ref"

    def __init__(self, model_name: str):
        self.model_name = model_name

    def __str__(self) -> str:
        return "ref('{}')".format(self.model_name)
