from datetime import date
from typing import TypeVar, TypedDict

from pydantic import BaseModel


class WildberriesCredentials(TypedDict):
    api_key: str
    type: str


IsSuccess = bool
Message = str
StartDate = date
EndDate = date

SchemaT = TypeVar("SchemaT", bound=BaseModel)
