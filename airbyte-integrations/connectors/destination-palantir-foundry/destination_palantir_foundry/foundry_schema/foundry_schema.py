from typing import List, Dict, Union, Literal, Annotated

from pydantic import BaseModel, Field, Discriminator


class ArrayFieldSchema(BaseModel):
    type_: Literal["ARRAY"] = Field("ARRAY", alias='type')
    name: str
    arraySubtype: 'FoundryFieldSchema'
    nullable: bool
    customMetadata: Dict = Field({})


class BinaryFieldSchema(BaseModel):
    type_: Literal["BINARY"] = Field("BINARY", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


class BooleanFieldSchema(BaseModel):
    type_: Literal["BOOLEAN"] = Field("BOOLEAN", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


class ByteFieldSchema(BaseModel):
    type_: Literal["BYTE"] = Field("BYTE", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


class DateFieldSchema(BaseModel):
    type_: Literal["DATE"] = Field("DATE", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


class DecimalFieldSchema(BaseModel):
    type_: Literal["DECIMAL"] = Field("DECIMAL", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})
    precision: int
    scale: int


class DoubleFieldSchema(BaseModel):
    type_: Literal["DOUBLE"] = Field("DOUBLE", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


class FloatFieldSchema(BaseModel):
    type_: Literal["FLOAT"] = Field("FLOAT", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


class IntegerFieldSchema(BaseModel):
    type_: Literal["INTEGER"] = Field("INTEGER", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


class LongFieldSchema(BaseModel):
    type_: Literal["LONG"] = Field("LONG", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


class MapFieldSchema(BaseModel):
    type_: Literal["MAP"] = Field("MAP", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})
    keyType: 'FoundryFieldSchema'
    valueType: 'FoundryFieldSchema'


class ShortFieldSchema(BaseModel):
    type_: Literal["SHORT"] = Field("SHORT", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


class StringFieldSchema(BaseModel):
    type_: Literal["STRING"] = Field("STRING", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


class StructFieldSchema(BaseModel):
    type_: Literal["STRUCT"] = Field("STRUCT", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})
    subSchemas: List['FoundryFieldSchema']


class TimestampFieldSchema(BaseModel):
    type_: Literal["TIMESTAMP"] = Field("TIMESTAMP", alias='type')
    name: str
    nullable: bool
    customMetadata: Dict = Field({})


FoundryFieldSchema = Annotated[Union[
    ArrayFieldSchema,
    BinaryFieldSchema,
    BooleanFieldSchema,
    ByteFieldSchema,
    DateFieldSchema,
    DecimalFieldSchema,
    DoubleFieldSchema,
    FloatFieldSchema,
    IntegerFieldSchema,
    LongFieldSchema,
    MapFieldSchema,
    ShortFieldSchema,
    StringFieldSchema,
    StructFieldSchema,
    TimestampFieldSchema,
], Discriminator(discriminator="type_")]


class FoundrySchema(BaseModel):
    fieldSchemaList: List[FoundryFieldSchema]
    dataFrameReaderClass: str
    customMetadata: Dict

# TODO(jcrowson): Subtypes don't need names, so can ignore in that case
