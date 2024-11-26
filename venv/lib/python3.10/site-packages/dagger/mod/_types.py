import dataclasses
from typing import TypeAlias

PythonName: TypeAlias = str
APIName: TypeAlias = str


@dataclasses.dataclass(slots=True)
class FieldDefinition:
    name: APIName | None
    optional: bool = False


@dataclasses.dataclass(slots=True, frozen=True)
class ObjectDefinition:
    name: PythonName
    doc: str | None = dataclasses.field(default=None, compare=False)
