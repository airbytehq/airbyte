# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""The base SQL Cache implementation."""

from __future__ import annotations

import abc
import contextlib
import enum
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Optional, cast, final

import pandas as pd
import sqlalchemy
import ulid
from airbyte import exceptions as exc
from airbyte._util.name_normalizers import LowerCaseNormalizer
from airbyte.constants import AB_EXTRACTED_AT_COLUMN, AB_META_COLUMN, AB_RAW_ID_COLUMN, DEBUG_MODE
# from airbyte.progress import progress
from airbyte.strategies import WriteStrategy
from airbyte.types import SQLTypeConverter
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from pandas import Index
from pydantic import BaseModel
from sqlalchemy import Column, Table, and_, create_engine, insert, null, select, text, update
from sqlalchemy.sql.elements import TextClause


from destination_mariadb.common.state.state_writers import StdOutStateWriter
from destination_mariadb.globals import DOCUMENT_ID_COLUMN

if TYPE_CHECKING:
    from collections.abc import Generator


    from airbyte._processors.file.base import FileWriterBase
    from airbyte.secrets.base import SecretString
    from airbyte_cdk.models import AirbyteRecordMessage
    from sqlalchemy.engine import Connection, Engine
    from sqlalchemy.engine.cursor import CursorResult
    from sqlalchemy.engine.reflection import Inspector
    from sqlalchemy.sql.base import Executable
    from sqlalchemy.sql.type_api import TypeEngine

    from destination_mariadb.common.catalog.catalog_providers import CatalogProvider
    from destination_mariadb.common.state.state_writers import StateWriterBase


class RecordDedupeMode(enum.Enum):
    APPEND = "append"
    REPLACE = "replace"




class SQLRuntimeError(Exception):
    """Raised when an SQL operation fails."""

class SqlConfig(BaseModel, abc.ABC):
    """Common configuration for SQL connections."""

    # schema_name: str
    # """The name of the schema to write to."""

    table_prefix: Optional[str] = ""
    """A prefix to add to created table names."""

    @abc.abstractmethod
    def get_sql_alchemy_url(self) -> SecretString:
        """Returns a SQL Alchemy URL."""
        ...

    @abc.abstractmethod
    def get_database_name(self) -> str:
        """Return the name of the database."""
        ...

    def connect(self) -> None:
        """Attempt to connect, and raise `AirbyteConnectionError` if the connection fails."""
        engine = self.get_sql_engine()
        try:
            connection = engine.connect()
            connection.close()
        except Exception as ex:
            raise exc.AirbyteConnectionError(
                message="Could not connect to the database.",
                guidance="Check the connection settings and try again.",
            ) from ex

    def get_sql_engine(self) -> Engine:
        """Return a new SQL engine to use."""
        return create_engine(
            url=self.get_sql_alchemy_url(),
            echo=DEBUG_MODE,
            # execution_options={
            #     "schema_translate_map": {None: self.schema_name},
            # },

        )

    def get_vendor_client(self) -> object:
        """Return the vendor-specific client object.

        This is used for vendor-specific operations.

        Raises `NotImplementedError` if a custom vendor client is not defined.
        """
        raise NotImplementedError(
            f"The type '{type(self).__name__}' does not define a custom client."
        )


class SqlProcessorBase(abc.ABC):
    """A base class to be used for SQL Caches."""

    type_converter_class: type[SQLTypeConverter] = SQLTypeConverter
    """The type converter class to use for converting JSON schema types to SQL types."""

    normalizer = LowerCaseNormalizer
    """The name normalizer to user for table and column name normalization."""


    """The file writer class to use for writing files to the cache."""

    supports_merge_insert = False
    """True if the database supports the MERGE INTO syntax."""

    # Constructor:

    def __init__(
        self,
        *,
        sql_config: SqlConfig,
        catalog_provider: CatalogProvider,
        state_writer: StateWriterBase | None = None,

    ) -> None:
        pass




