"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import pkgutil
import shutil
from pathlib import Path
from typing import Dict

from airbyte_protocol import ConfiguredAirbyteCatalog, ConnectorSpecification
from base_python_test import StandardSourceTestIface
from google_sheets_source.client import GoogleSheetsClient
from google_sheets_source.helpers import Helpers
from google_sheets_source.models.spreadsheet import Spreadsheet

# Override default permission scopes to allow creating and editing spreadsheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]


class GoogleSheetsSourceStandardTest(StandardSourceTestIface):
    def __init__(self):
        pass

    def get_spec(self) -> ConnectorSpecification:
        raw_spec = pkgutil.get_data(self.__class__.__module__.split(".")[0], "spec.json")
        return ConnectorSpecification.parse_obj(json.loads(raw_spec))

    def get_config(self) -> object:
        config = {"credentials_json": json.dumps(self._get_creds()), "spreadsheet_id": self._get_spreadsheet_id()}
        return config

    def get_catalog(self) -> ConfiguredAirbyteCatalog:
        raw_catalog = pkgutil.get_data(self.__class__.__module__.split(".")[0], "configured_catalog.json")
        return ConfiguredAirbyteCatalog.parse_obj(json.loads(raw_catalog))

    def setup(self) -> None:
        Path(self._get_tmp_dir()).mkdir(parents=True, exist_ok=True)

        sheets_client = GoogleSheetsClient(self._get_creds(), SCOPES)
        spreadsheet_id = self._create_spreadsheet(sheets_client)
        self._write_spreadsheet_id(spreadsheet_id)

    def teardown(self) -> None:
        drive_client = Helpers.get_authenticated_drive_client(self._get_creds(), SCOPES)
        drive_client.files().delete(fileId=self._get_spreadsheet_id()).execute()
        shutil.rmtree(self._get_tmp_dir(), ignore_errors=True)

    def _get_spreadsheet_id_file_path(self):
        return str(Path(self._get_tmp_dir()) / "spreadsheet_id.txt")

    def _write_spreadsheet_id(self, spreadsheet_id: str):
        with open(self._get_spreadsheet_id_file_path(), "w") as file:
            file.write(spreadsheet_id)

    def _get_spreadsheet_id(self):
        with open(self._get_spreadsheet_id_file_path(), "r") as file:
            return file.read()

    def _get_creds(self) -> Dict[str, str]:
        return json.loads(pkgutil.get_data(self.__class__.__module__.split(".")[0], "creds.json"))

    # TODO this should be provided by the super class
    @staticmethod
    def _get_tmp_dir():
        return "/test_root/gsheet_test"

    def _create_spreadsheet(self, sheets_client: GoogleSheetsClient) -> str:
        """
        :return: spreadsheetId
        """
        request = {
            "properties": {"title": "integration_test_spreadsheet"},
            "sheets": [{"properties": {"title": "sheet1"}}, {"properties": {"title": "sheet2"}}],
        }

        spreadsheet = Spreadsheet.parse_obj(sheets_client.create(body=request))
        spreadsheet_id = spreadsheet.spreadsheetId

        rows = [["header1", "irrelevant", "header3", "", "ignored"]]
        rows.extend([f"a{i}", "dontmindme", i] for i in range(300))
        rows.append(["lonely_left_value", "", ""])
        rows.append(["", "", "lonelyrightvalue"])
        rows.append(["", "", ""])
        rows.append(["orphan1", "orphan2", "orphan3"])

        sheets_client.update_values(
            spreadsheetId=spreadsheet_id,
            body={"data": {"majorDimension": "ROWS", "values": rows, "range": "sheet1"}, "valueInputOption": "RAW"},
        )
        sheets_client.update_values(
            spreadsheetId=spreadsheet_id,
            body={"data": {"majorDimension": "ROWS", "values": rows, "range": "sheet2"}, "valueInputOption": "RAW"},
        )

        return spreadsheet_id
