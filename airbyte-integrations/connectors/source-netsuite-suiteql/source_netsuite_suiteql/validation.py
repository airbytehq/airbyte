# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import re
from typing import Any, Iterable, Mapping, TypedDict

from typing_extensions import NotRequired

from airbyte_cdk.models import ConfiguredAirbyteStream, SyncMode

from .errors import (
    InvalidIdentifierError,
    InvalidRealmError,
    MissingCatalogCursorFieldError,
    MultipleCatalogFieldsError,
    NestedCatalogFieldError,
)


IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
REALM_PATTERN = re.compile(r"^[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*$")


class SuiteQLTableFields(TypedDict):
    primary_key: list[str]
    cursor_field: str | None


class SuiteQLTableConfig(TypedDict):
    table_name: str
    primary_key: NotRequired[list[str]]
    cursor_field: NotRequired[str | None]


class SuiteQLSourceConfig(TypedDict):
    realm: str
    consumer_key: str
    consumer_secret: str
    token_key: str
    token_secret: str
    tables: list[SuiteQLTableConfig]
    page_size: NotRequired[int]


class SuiteQLIdentifierValidator:
    @staticmethod
    def validate(identifiers: Iterable[str]) -> None:
        invalid_identifiers = [identifier for identifier in identifiers if not IDENTIFIER_PATTERN.fullmatch(identifier)]
        if invalid_identifiers:
            raise InvalidIdentifierError(invalid_identifiers)


class SuiteQLRealmValidator:
    @staticmethod
    def validate(realm: str) -> None:
        if not REALM_PATTERN.fullmatch(realm):
            raise InvalidRealmError(realm)


class SuiteQLTableValidator:
    def __init__(self, table: Mapping[str, Any]):
        self.table = table

    def validate(self) -> None:
        identifiers = [
            self.table["table_name"],
            *self.table.get("primary_key", []),
        ]
        if cursor_field := self.table.get("cursor_field"):
            identifiers.append(cursor_field)

        SuiteQLIdentifierValidator.validate(identifiers)


class SuiteQLCatalogStreamValidator:
    def __init__(self, configured_stream: ConfiguredAirbyteStream) -> None:
        self.configured_stream = configured_stream

    def table_fields(self) -> SuiteQLTableFields:
        """Return the catalog fields used to build this stream's SuiteQL query.

        Examples:
        - `primary_key=[["id"]]` -> `primary_key=["id"]`.
        - `cursor_field=["lastmodifieddate"]` -> `cursor_field="lastmodifieddate"`.
        - A full-refresh stream without a cursor returns `cursor_field=None`.

        Nested field paths and multiple cursor fields are unsupported by SuiteQL.
        """
        configured_key = self.configured_stream.primary_key or []
        configured_cursor = self.configured_stream.cursor_field or []

        primary_key = self._top_level_fields(configured_key, "primary key")
        cursor_field = self._single_top_level_field(configured_cursor, "cursor field")

        identifiers = [*primary_key]
        if cursor_field is not None:
            identifiers.append(cursor_field)

        SuiteQLIdentifierValidator.validate(identifiers)

        if self.configured_stream.sync_mode == SyncMode.incremental and not cursor_field:
            raise MissingCatalogCursorFieldError(self.configured_stream.stream.name)

        return SuiteQLTableFields(
            primary_key=primary_key,
            cursor_field=cursor_field,
        )

    def _top_level_fields(self, fields: list[list[str]], field_type: str) -> list[str]:
        if any(len(field) != 1 for field in fields):
            raise NestedCatalogFieldError(field_type)
        return [field[0] for field in fields]

    def _single_top_level_field(self, fields: list[str], field_type: str) -> str | None:
        if len(fields) > 1:
            raise MultipleCatalogFieldsError(field_type)
        return fields[0] if fields else None
