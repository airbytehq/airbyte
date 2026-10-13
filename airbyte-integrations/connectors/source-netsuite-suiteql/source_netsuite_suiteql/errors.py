# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import requests


class DuplicateTableNameError(ValueError):
    def __init__(self, names: list[str]) -> None:
        super().__init__(f"Duplicate table names: {', '.join(sorted(names))}")


class InvalidIdentifierError(ValueError):
    def __init__(self, identifiers: list[str]) -> None:
        super().__init__(
            "Table names, primary keys, and cursor fields must start with a letter or underscore and contain only letters, numbers, and underscores: "
            + ", ".join(identifiers)
        )


class InvalidRealmError(ValueError):
    def __init__(self, realm: str) -> None:
        super().__init__(f"Invalid NetSuite account ID: {realm}")


class MissingCursorFieldError(ValueError):
    def __init__(self, cursor_field: str) -> None:
        super().__init__(f"Incremental table record is missing cursor field '{cursor_field}'.")


class MissingCatalogCursorFieldError(ValueError):
    def __init__(self, stream_name: str) -> None:
        super().__init__(f"Incremental stream '{stream_name}' requires a cursor field.")


class NestedCatalogFieldError(ValueError):
    def __init__(self, field_type: str) -> None:
        super().__init__(f"NetSuite SuiteQL does not support nested {field_type} fields.")


class MultipleCatalogFieldsError(ValueError):
    def __init__(self, field_type: str) -> None:
        super().__init__(f"NetSuite SuiteQL supports only one {field_type}.")


def raise_for_netsuite_status(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        try:
            details = response.json().get("o:errorDetails", [])
            message = "; ".join(detail.get("detail", "") for detail in details if detail.get("detail"))
        except ValueError:
            message = response.text
        if message:
            raise requests.HTTPError(f"{error} NetSuite error: {message}", response=response) from error
        raise
