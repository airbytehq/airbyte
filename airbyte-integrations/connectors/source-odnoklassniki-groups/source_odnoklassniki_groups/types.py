from datetime import date
from typing import TypeVar

from pydantic import BaseModel

IsSuccess = bool
Message = str
StartDate = date
EndDate = date

SchemaT = TypeVar("SchemaT", bound=BaseModel)
