from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class FoundryFieldType(str, Enum):
    # ARRAY = "ARRAY" TODO
    BINARY = "BINARY"
    BOOLEAN = "BOOLEAN"
    BYTE = "BYTE"
    DATE = "DATE"
    # DECIMAL = "DECIMAL" TODO
    DOUBLE = "DOUBLE"
    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    LONG = "LONG"
    # MAP = "MAP" TODO
    SHORT = "SHORT"
    STRING = "STRING"
    # STRUCT = "STRUCT" TODO
    TIMESTAMP = "TIMESTAMP"


class FoundryFieldSchema(BaseModel):
    type_: FoundryFieldType = Field(..., alias='type')
    name: str
    nullable: bool
    customMetadata: Dict


class FoundrySchema(BaseModel):
    fieldSchemaList: List[FoundryFieldSchema]
    dataFrameReaderClass: str
    customMetadata: Dict
