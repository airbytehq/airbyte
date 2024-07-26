from abc import abstractmethod
from typing import List, Dict, Union, Literal, Annotated, Optional

from pydantic import BaseModel, Field, Discriminator, model_serializer


class FoundryFieldSchemaBase(BaseModel):
    name: Optional[str] = Field(None)
    nullable: bool
    customMetadata: Dict = Field({})

    def _base_to_dict(self):
        dict_rep = {
            "nullable": self.nullable,
            "customMetadata": self.customMetadata,
        }

        if self.name is not None:
            dict_rep["name"] = self.name

        return dict_rep

    @abstractmethod
    def ser(self):
        pass


class ArrayFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["ARRAY"] = Field("ARRAY", alias='type')
    arraySubtype: 'FoundryFieldSchema'

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
            "arraySubtype": self.arraySubtype.ser()
        }


class BinaryFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["BINARY"] = Field("BINARY", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


class BooleanFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["BOOLEAN"] = Field("BOOLEAN", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


class ByteFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["BYTE"] = Field("BYTE", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


class DateFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["DATE"] = Field("DATE", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


class DecimalFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["DECIMAL"] = Field("DECIMAL", alias='type')
    precision: int
    scale: int

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
            "precision": self.precision,
            "scale": self.scale
        }


class DoubleFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["DOUBLE"] = Field("DOUBLE", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


class FloatFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["FLOAT"] = Field("FLOAT", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


class IntegerFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["INTEGER"] = Field("INTEGER", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


class LongFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["LONG"] = Field("LONG", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


class MapFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["MAP"] = Field("MAP", alias='type')
    keyType: 'FoundryFieldSchema'
    valueType: 'FoundryFieldSchema'

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
            "keyType": self.keyType.ser(),
            "valueType": self.valueType.ser()
        }


class ShortFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["SHORT"] = Field("SHORT", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


class StringFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["STRING"] = Field("STRING", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


class StructFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["STRUCT"] = Field("STRUCT", alias='type')
    subSchemas: List['FoundryFieldSchema']

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
            "subSchemas": [sub_schema.ser() for sub_schema in self.subSchemas]
        }


class TimestampFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["TIMESTAMP"] = Field("TIMESTAMP", alias='type')

    @model_serializer
    def ser(self):
        return {
            **self._base_to_dict(),
            "type": self.type_,
        }


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

    @model_serializer
    def ser(self):
        return {
            "fieldSchemaList": [field.ser() for field in self.fieldSchemaList],
            "dataFrameReaderClass": self.dataFrameReaderClass,
            "customMetadata": self.customMetadata
        }

# TODO(jcrowson): Subtypes don't need names, so can ignore in that case
