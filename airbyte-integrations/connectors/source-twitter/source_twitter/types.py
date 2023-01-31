from datetime import date
from typing import TypeVar, TypedDict

from pydantic import BaseModel


class TwitterCredentials(TypedDict):
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str


IsSuccess = bool
Message = str
StartDate = date
EndDate = date

SchemaT = TypeVar("SchemaT", bound=BaseModel)
