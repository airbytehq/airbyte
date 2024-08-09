#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import logging
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import pandas as pd
import numpy as np
from python_calamine import CalamineWorkbook
from python_calamine.pandas import pandas_monkeypatch
from pandas.io.json._table_schema import build_table_schema
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import SchemaType
from airbyte_cdk.sources.file_based.config.xlsx_format import XlsxFormat


class XlsxParser(FileTypeParser):

    def check_config(self, config: FileBasedStreamConfig) -> Tuple[bool, Optional[str]]:
        """
        JsonlParser does not require config checks, implicit pydantic validation is enough.
        """
        return True, None

    async def infer_schema(
            self,
            config: FileBasedStreamConfig,
            file: RemoteFile,
            stream_reader: AbstractFileBasedStreamReader,
            logger: logging.Logger,
    ) -> SchemaType:
        pandas_monkeypatch()
        xlsx_format = config.format
        if not isinstance(xlsx_format, XlsxFormat):
            raise ValueError(f"Expected XlsxFormat, got {xlsx_format}")
        sheet_selector = int(xlsx_format.sheet_name) if xlsx_format.sheet_name.isdigit() else xlsx_format.sheet_name
        sheet = pd.read_excel(stream_reader.open_file(file, self.file_read_mode, None, logger),
                              sheet_name=sheet_selector, engine="calamine")
        schema = {x['name']:{'type':x['type']} for x in build_table_schema(sheet, index=False)['fields']}
        schema['sheet_row_number'] = {'type':'integer'}
        return schema

    def parse_records(
            self,
            config: FileBasedStreamConfig,
            file: RemoteFile,
            stream_reader: AbstractFileBasedStreamReader,
            logger: logging.Logger,
            discovered_schema: Optional[Mapping[str, SchemaType]],
    ) -> Iterable[Dict[str, Any]]:
        xlsx_format = config.format
        if not isinstance(xlsx_format, XlsxFormat):
            raise ValueError(f"Expected XlsxFormat, got {xlsx_format}")
        sheet_selector = int(xlsx_format.sheet_name) if xlsx_format.sheet_name.isdigit() else xlsx_format.sheet_name
        pandas_monkeypatch()
        sheet = pd.read_excel(stream_reader.open_file(file, self.file_read_mode, None, logger), sheet_name=sheet_selector, engine="calamine")
        for row_number, row in enumerate(sheet.replace({np.nan: None}).to_dict(orient="records")):
            row['sheet_row_number'] = row_number
            yield row

    @property
    def file_read_mode(self) -> FileReadMode:
        return FileReadMode.READ_BINARY
