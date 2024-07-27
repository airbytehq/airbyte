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
        # HACKHACK: Needed since we can't control how foundry platform sdk serializes these objects
        pass


class ArrayFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["ARRAY"] = Field("ARRAY", alias='type')
    arraySubtype: 'FoundryFieldSchema' = Field(...)

    @model_serializer
    def ser(self):
        print(self)
        return {
            **self._base_to_dict(),
            "type": self.type_,
            "arraySubtype": self.arraySubtype.ser()
        }


class BooleanFieldSchema(FoundryFieldSchemaBase):
    type_: Literal["BOOLEAN"] = Field("BOOLEAN", alias='type')

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
    BooleanFieldSchema,
    DateFieldSchema,
    DoubleFieldSchema,
    FloatFieldSchema,
    IntegerFieldSchema,
    LongFieldSchema,
    StringFieldSchema,
    StructFieldSchema,
    TimestampFieldSchema,
], Discriminator(discriminator="type_")]


class FoundrySchema(BaseModel):
    fieldSchemaList: List[FoundryFieldSchema]
    dataFrameReaderClass: str
    customMetadata: Dict
