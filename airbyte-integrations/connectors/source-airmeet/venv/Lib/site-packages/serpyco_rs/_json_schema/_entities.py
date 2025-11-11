from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._consts import DEFAULT_REF_PREFIX


@dataclass
class Config:
    ref_prefix: str = DEFAULT_REF_PREFIX


@dataclass
class Schema:
    config: Config

    type: str | None = None
    title: str | None = None
    description: str | None = None
    default: Any | None = None
    enum: list[Any] | None = None

    allOf: list[Schema] | None = None
    anyOf: list[Schema] | None = None
    oneOf: list[Schema] | None = None
    additionalArgs: dict[str, Any] | None = None

    def dump(self, definitions: dict[str, Any]) -> dict[str, Any]:
        data = {
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'default': self.default,
            'enum': self.enum,
            'allOf': [item.dump(definitions) for item in self.allOf] if self.allOf else None,
            'anyOf': [item.dump(definitions) for item in self.anyOf] if self.anyOf else None,
            'oneOf': [item.dump(definitions) for item in self.oneOf] if self.oneOf else None,
            **(self.additionalArgs or {}),
        }
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class Boolean(Schema):
    type: str = 'boolean'  # pyright: ignore[reportIncompatibleVariableOverride]


@dataclass
class Null(Schema):
    type: str = 'null'  # pyright: ignore[reportIncompatibleVariableOverride]


@dataclass
class StringType(Schema):
    type: str = 'string'  # pyright: ignore[reportIncompatibleVariableOverride]
    minLength: int | None = None
    maxLength: int | None = None
    format: str | None = None

    def dump(self, definitions: dict[str, Any]) -> dict[str, Any]:
        data = super().dump(definitions)
        data = {
            'minLength': self.minLength,
            'maxLength': self.maxLength,
            'format': self.format,
            **data,
        }
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class NumberType(Schema):
    type: str = 'number'  # pyright: ignore[reportIncompatibleVariableOverride]
    minimum: float | None = None
    maximum: float | None = None
    format: str | None = None

    def dump(self, definitions: dict[str, Any]) -> dict[str, Any]:
        data = super().dump(definitions)
        data = {
            'minimum': self.minimum,
            'maximum': self.maximum,
            'format': self.format,
            **data,
        }
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class IntegerType(NumberType):
    type: str = 'integer'
    format: str | None = 'int64'


@dataclass
class ObjectType(Schema):
    name: str | None = None
    type: str = 'object'  # pyright: ignore[reportIncompatibleVariableOverride]
    properties: dict[str, Schema] | None = None
    additionalProperties: bool | Schema | None = None
    required: list[str] | None = None

    @property
    def ref(self) -> str:
        return f'{self.config.ref_prefix}/{self.name}'

    def dump(self, definitions: dict[str, Any]) -> dict[str, Any]:
        data = super().dump(definitions)
        data = {
            'properties': {k: v.dump(definitions) for k, v in self.properties.items()} if self.properties else None,
            'additionalProperties': self._resolve_additional_properties(definitions),
            'required': self.required,
            **data,
        }
        data = {k: v for k, v in data.items() if v is not None}
        if not self.name:
            return data
        definitions[self.name] = data
        return {
            '$ref': self.ref,
        }

    def _resolve_additional_properties(self, definitions: dict[str, Any]) -> bool | dict[str, Any] | None:
        if not isinstance(self.additionalProperties, Schema):
            return self.additionalProperties
        schema_data = self.additionalProperties.dump(definitions)
        return True if schema_data == {} else schema_data


@dataclass
class ArrayType(Schema):
    type: str = 'array'  # pyright: ignore[reportIncompatibleVariableOverride]
    items: Schema | None = None
    prefixItems: list[Schema] | None = None
    minItems: int | None = None
    maxItems: int | None = None

    def dump(self, definitions: dict[str, Any]) -> dict[str, Any]:
        data = super().dump(definitions)
        data = {
            'items': self.items.dump(definitions) if self.items else None,
            'prefixItems': [i.dump(definitions) for i in self.prefixItems] if self.prefixItems else None,
            'minItems': self.minItems,
            'maxItems': self.maxItems,
            **data,
        }
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class RefType(Schema):
    name: str | None = None
    definition: Schema | None = None

    @property
    def ref(self) -> str:
        return f'{self.config.ref_prefix}/{self.name}'

    def dump(self, definitions: dict[str, Any]) -> dict[str, Any]:
        data = super().dump(definitions)
        if self.definition:
            assert self.name
            definitions[self.name] = self.definition.dump(definitions)
        return {
            '$ref': self.ref,
            **data,
        }


@dataclass
class DiscriminatedUnionType(Schema):
    discriminator: Discriminator | None = None

    def dump(self, definitions: dict[str, Any]) -> dict[str, Any]:
        data = super().dump(definitions)
        return {
            'discriminator': self.discriminator.dump() if self.discriminator else None,
            **data,
        }


@dataclass
class Discriminator:
    property_name: str
    mapping: dict[str, str]

    def dump(self) -> dict[str, Any]:
        return {
            'propertyName': self.property_name,
            'mapping': self.mapping,
        }
