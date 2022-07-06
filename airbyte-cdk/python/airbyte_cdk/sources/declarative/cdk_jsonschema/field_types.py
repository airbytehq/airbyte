#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import warnings
from datetime import date, datetime
from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address
from typing import Generic, Optional, TypeVar, cast
from uuid import UUID

from dateutil.parser import parse

from .type_defs import JsonDict, JsonEncodable

T = TypeVar("T")
OutType = TypeVar("OutType", bound=JsonEncodable)


class FieldEncoder(Generic[T, OutType]):
    """Base class for encoding fields to and from JSON encodable values"""

    def to_wire(self, value: T) -> OutType:
        return cast(OutType, value)

    def to_python(self, value: OutType) -> T:
        return cast(T, value)

    @property
    def json_schema(self) -> JsonDict:
        raise NotImplementedError()


class DateFieldEncoder(FieldEncoder[date, str]):
    """Encodes dates to RFC3339 format"""

    def to_wire(self, value: date) -> str:
        return value.isoformat()

    def to_python(self, value: str) -> date:
        return value if isinstance(value, date) else parse(cast(str, value)).date()

    @property
    def json_schema(self) -> JsonDict:
        return {"type": "string", "format": "date"}


class DateTimeFieldEncoder(FieldEncoder[datetime, str]):
    """Encodes datetimes to RFC3339 format"""

    def to_wire(self, value: datetime) -> str:
        out = value.isoformat()

        # Assume UTC if timezone is missing
        if value.tzinfo is None:
            warnings.warn("Naive datetime used, assuming utc")
            return out + "Z"
        return out

    def to_python(self, value: str) -> datetime:
        return value if isinstance(value, datetime) else parse(cast(str, value))

    @property
    def json_schema(self) -> JsonDict:
        return {"type": "string", "format": "date-time"}


# Alias for backwards compat
DateTimeField = DateTimeFieldEncoder
UUID_REGEX = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


class UuidField(FieldEncoder[UUID, str]):
    def to_wire(self, value: UUID) -> str:
        return str(value)

    def to_python(self, value: str) -> UUID:
        return UUID(value)

    @property
    def json_schema(self):
        return {"type": "string", "format": "uuid", "pattern": UUID_REGEX}


class DecimalField(FieldEncoder[Decimal, float]):
    def __init__(self, precision: Optional[int] = None):
        self.precision = precision

    def to_wire(self, value: Decimal) -> float:
        return float(value)

    def to_python(self, value: float) -> Decimal:
        return Decimal(str(value))

    @property
    def json_schema(self):
        schema = {"type": "number"}
        if self.precision is not None and self.precision > 0:
            schema["multipleOf"] = float("0." + "0" * (self.precision - 1) + "1")
        return schema


class IPv4AddressField(FieldEncoder[IPv4Address, str]):
    def to_wire(self, value: IPv4Address) -> str:
        return str(value)

    def to_python(self, value: str) -> IPv4Address:
        return IPv4Address(value)

    @property
    def json_schema(self):
        return {"type": "string", "format": "ipv4"}


class IPv6AddressField(FieldEncoder[IPv6Address, str]):
    def to_wire(self, value: IPv6Address) -> str:
        return str(value)

    def to_python(self, value: str) -> IPv6Address:
        return IPv6Address(value)

    @property
    def json_schema(self):
        return {"type": "string", "format": "ipv6"}
