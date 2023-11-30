from typing import Sequence

from pydantic import BaseModel


class BaseOzonReport(BaseModel):
    @classmethod
    def from_list_of_values(cls, values: Sequence) -> "BaseOzonReport":
        return cls.parse_obj(dict(zip(cls.__fields__.keys(), values)))
